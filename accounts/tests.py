from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

PASSWORD = "S3cure!Passw0rd"


class AuthFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jane@example.com",
            email="jane@example.com",
            password=PASSWORD,
            first_name="Jane",
            last_name="Doe",
        )

    def test_auth_pages_render(self):
        for name in ("login", "signup"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/auth.html")

    def test_root_redirects_by_auth_state(self):
        self.assertRedirects(self.client.get(reverse("home")), reverse("login"))
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(reverse("home")), reverse("success"))

    def test_success_requires_login(self):
        response = self.client.get(reverse("success"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('success')}",
            fetch_redirect_response=False,
        )

    def test_signup_lowercases_email_and_signs_in(self):
        response = self.client.post(
            reverse("signup"),
            {
                "first_name": "Sam",
                "last_name": "Lee",
                "email": "Sam.Lee@Example.com",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertRedirects(
            response, reverse("success"), fetch_redirect_response=False
        )

        user = User.objects.get(username="sam.lee@example.com")
        self.assertEqual(user.email, "sam.lee@example.com")
        self.assertEqual(user.get_full_name(), "Sam Lee")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

        for _ in range(2):
            response = self.client.get(reverse("success"))
            self.assertContains(response, "Account created successfully")
            self.assertContains(response, "sam.lee@example.com")

    def test_signup_requires_names_and_email(self):
        data = {
            "first_name": "Sam",
            "last_name": "Lee",
            "email": "sam@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        for field, value in (
            ("first_name", ""),
            ("last_name", ""),
            ("email", "   "),
            ("email", "not-an-email"),
            ("email", "a" * 145 + "@example.com"),
        ):
            with self.subTest(field=field, value=value):
                response = self.client.post(
                    reverse("signup"), {**data, field: value}
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
                self.assertEqual(User.objects.count(), 1)

    def test_signup_rejects_duplicate_email_ignoring_case(self):
        response = self.client.post(
            reverse("signup"),
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "  JANE@example.com  ",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_signup_validates_password(self):
        cases = [
            (PASSWORD, "Different!Pass1", "password2"),
            ("12345678", "12345678", "password1"),
        ]
        for password1, password2, field in cases:
            with self.subTest(field=field):
                response = self.client.post(
                    reverse("signup"),
                    {
                        "first_name": "Sam",
                        "last_name": "Lee",
                        "email": f"sam-{field}@example.com",
                        "password1": password1,
                        "password2": password2,
                    },
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
                self.assertFalse(User.objects.filter(email__startswith="sam-").exists())

    def test_login_ignores_email_case(self):
        response = self.client.post(
            reverse("login"),
            {"username": "JANE@EXAMPLE.COM", "password": PASSWORD},
        )
        self.assertRedirects(response, reverse("success"))
        response = self.client.get(reverse("success"))
        self.assertContains(response, "Signed in successfully")

    def test_signup_message_survives_refresh_and_changes_after_login(self):
        self.client.post(
            reverse("signup"),
            {
                "first_name": "Sam",
                "last_name": "Lee",
                "email": "sam@example.com",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertContains(
            self.client.get(reverse("success")), "Account created successfully"
        )
        self.assertContains(
            self.client.get(reverse("success")), "Account created successfully"
        )

        self.client.post(reverse("logout"))
        self.client.post(
            reverse("login"),
            {"username": "sam@example.com", "password": PASSWORD},
        )
        response = self.client.get(reverse("success"))
        self.assertContains(response, "Signed in successfully")
        self.assertNotContains(response, "Account created successfully")

    def test_success_page_escapes_names(self):
        self.client.post(
            reverse("signup"),
            {
                "first_name": "<script>alert(1)</script>",
                "last_name": "Lee",
                "email": "script@example.com",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        response = self.client.get(reverse("success"))
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")

    def test_login_rejects_bad_password(self):
        response = self.client.post(
            reverse("login"),
            {"username": "jane@example.com", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email or password is incorrect")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post_and_ends_session(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_signed_in_users_skip_auth_pages(self):
        self.client.force_login(self.user)
        for name in ("login", "signup"):
            self.assertRedirects(self.client.get(reverse(name)), reverse("success"))
