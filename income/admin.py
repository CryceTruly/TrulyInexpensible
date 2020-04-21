from django.contrib import admin
from .models import Income, Source
# Register your models here.


class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'currency', 'source', 'created_at', 'owner',)
    search_fields = ('amount', 'currency', 'source', 'created_at', 'owner',)
    list_per_page = 25


admin.site.register(Source)
admin.site.register(Income, IncomeAdmin)
