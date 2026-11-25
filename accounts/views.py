from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignupForm


def home(request):
    return redirect("success" if request.user.is_authenticated else "login")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("success")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        request.session["auth_event"] = "login"
        return redirect("success")

    return render(
        request,
        "accounts/auth.html",
        {
            "form": form,
            "is_signup": False,
            "heading": "Sign in",
            "subtitle": "Enter your personal details to access your account",
            "submit_label": "Sign in",
            "social_prefix": "Sign in",
            "switch_text": "Don't have an account?",
            "switch_link": "Sign up",
            "switch_url": reverse("signup"),
        },
    )


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("success")

    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        request.session["auth_event"] = "signup"
        return redirect("success")

    return render(
        request,
        "accounts/auth.html",
        {
            "form": form,
            "is_signup": True,
            "heading": "Sign up",
            "subtitle": "Enter your personal details to create your account",
            "submit_label": "Sign up",
            "social_prefix": "Sign up",
            "switch_text": "Already have an account?",
            "switch_link": "Sign in",
            "switch_url": reverse("login"),
        },
    )


@login_required
def success_view(request):
    created = request.session.get("auth_event", "login") == "signup"
    return render(
        request,
        "accounts/success.html",
        {
            "heading": "Account created successfully" if created else "Signed in successfully",
            "created": created,
        },
    )


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")
