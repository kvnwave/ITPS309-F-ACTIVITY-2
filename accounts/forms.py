from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q


class SignupForm(UserCreationForm):
    # User.email is optional on the model, but it is the login ID here.
    email = forms.EmailField(
        label="Email",
        max_length=150,
        widget=forms.EmailInput(
            attrs={"placeholder": "janedoe@gmail.com", "autocomplete": "email"}
        ),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First name",
                    "autocomplete": "given-name",
                    "autofocus": True,
                }
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Last name", "autocomplete": "family-name"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name"):
            self.fields[name].required = True
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm password"
        for name in ("password1", "password2"):
            self.fields[name].widget.attrs["placeholder"] = "**********"
            self.fields[name].help_text = ""

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(
            Q(username__iexact=email) | Q(email__iexact=email)
        ).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def validate_password_for_user(self, user):
        # Attach password errors to password1 instead of Django's default password2.
        super().validate_password_for_user(user, password_field_name="password1")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        max_length=150,
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "autocomplete": "email",
                "placeholder": "janedoe@gmail.com",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "placeholder": "**********"}
        ),
    )
    error_messages = {
        "invalid_login": "Email or password is incorrect. Please try again.",
        "inactive": "This account is inactive.",
    }

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()
