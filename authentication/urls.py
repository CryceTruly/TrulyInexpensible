from . import views
from django.urls import path, include
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout, name="logout"),
    path('activate/<uidb64>/<token>',
         views.VerificationView.as_view(), name='activate'),
    path('', login_required(views.ProfileView.as_view()), name='home'),
    path('request-reset', views.RequestResetLinkView.as_view(),
         name='reset-password'),
    path('change-password/<uidb64>/<token>',
         views.CompletePasswordChangeView.as_view(), name='change-password'),
]
