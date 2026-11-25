from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("success/", views.success_view, name="success"),
    path("logout/", views.logout_view, name="logout"),
]
