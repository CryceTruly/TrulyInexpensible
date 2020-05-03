from . import views
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path("login", views.LoginView.as_view(), name="login"),
    path("register", views.RegistrationView.as_view(), name="register"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path('activate/<uidb64>/<token>',
         views.VerificationView.as_view(), name='activate'),
    path('request-reset', views.RequestResetLinkView.as_view(),
         name='reset-password'),
    path('change-password/<uidb64>/<token>',
         views.CompletePasswordChangeView.as_view(), name='change-password'),
    path('check_email', csrf_exempt(
        views.CredentialsValidationView.as_view()), name='validate-email'),

    path('check_username', csrf_exempt(
        views.UsernameValidationView.as_view()), name='validate-username'),
]
