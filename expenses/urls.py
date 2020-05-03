from django.urls import path
from . import views


urlpatterns = [

    path("", views.expenses, name="expenses"),
    path("expenses_add", views.expenses_add, name="expenses_add"),
    path("expense_detail", views.expense_detail, name="expense_detail"),
    path("summary", views.expense_summary, name="expenses-summary"),
    path("expense_edit/<int:id>", views.expense_edit, name="expense_edit"),
    path("expense_delete/<int:id>", views.expense_delete, name="expense_delete"),
    path('expenses/search_expenses', views.search_expenses, name='search_expenses'),
    path('expenses/summary_rest', views.expense_summary_rest,
         name='expenses_summary_rest'),
    path('expenses/three_months_summary', views.last_3months_stats,
         name='three_months_summary'),

    path('expenses/last_3months_expense_source_stats',
         views.last_3months_expense_source_stats, name="last_3months_expense_source_stats")
]
