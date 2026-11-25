# ITPS309 Activity 2 — Django Account System

A small Django sign-up / sign-in app. It uses Django's built-in authentication system, the
default `User` model, and a local SQLite database.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Use `/admin/` to inspect accounts (run
`python manage.py createsuperuser` once to get an admin login).

## Routes

| Route | Purpose |
| --- | --- |
| `/login/` | Sign in with email + password |
| `/signup/` | Create an account |
| `/success/` | Protected success page (also the post-login destination) |
| `/logout/` | POST-only sign out |

The root URL redirects to the correct page based on whether you are signed in.

## Notes

- Email addresses are the login ID. They are trimmed, lowercased, and stored as
  both Django's `username` and `email`, so `Jane@Example.com` and
  `jane@example.com` are the same account.
- Passwords use Django's default validators: at least 8 characters, not too
  common, and not entirely numeric.
- Signing up logs you in automatically and shows the shared success page with
  "Account created successfully"; signing in shows "Signed in successfully".
- The Google and Facebook buttons are intentionally disabled; no third-party
  login is configured.
- The four left-hand tiles are placeholders, as in the mockups.

## Tests

```bash
python manage.py test
```

The suite covers sign-up, duplicate email handling, password validation,
sign-in, the protected success page, and POST-only logout.
