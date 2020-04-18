from django.contrib import admin
from .models import Expense, Category
# Register your models here.


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'currency',
                    'date', 'category', 'owner',)
    search_fields = ('name', 'amount', 'currency',
                     'date', 'category', 'owner',)
    list_per_page = 25


admin.site.register(Category)
admin.site.register(Expense, ExpenseAdmin)
