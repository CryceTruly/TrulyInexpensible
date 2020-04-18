from django.urls import path
from . import views


urlpatterns = [
    path("income", views.income, name="income"),
    path("income-summary", views.income_summary, name="income-summary"),

]
