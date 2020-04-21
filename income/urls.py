from django.urls import path
from . import views


urlpatterns = [
    path("", views.income, name="income"),
    path("income-summary", views.income_summary, name="income-summary"),
    path("income_add", views.income_add, name="income_add"),
    path("income_detail", views.income_detail, name="income_detail"),
    path("income_edit<int:id>", views.income_edit, name="income_edit"),
    path("income_delete<int:id>", views.income_delete, name="income_delete"),
    path('search_income', views.search_income, name='search_income'),
    path('summary_rest', views.income_summary_rest,
         name='income_summary_rest'),
    path('three_months_summary', views.last_3months_income_stats,
         name='three_months_summary_'),
    path('last_3months_income_source_stats', views.last_3months_income_source_stats,
         name='last_3months_income_source_stats_'),

]
