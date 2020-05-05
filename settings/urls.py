from .views import index, account
from django.urls import path
urlpatterns = [
    path('general', index, name="general-settings"),
    path('account', index, name="account-settings")
]
