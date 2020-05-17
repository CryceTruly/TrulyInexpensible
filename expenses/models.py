from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import now


class Expense(models.Model):
    name = models.CharField(max_length=255, db_index=True, default='')
    date = models.DateField(default=now)
    amount = models.FloatField(blank=False, null=False)
    currency = models.CharField(max_length=20, default="USD")
    category = models.CharField(max_length=255)
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date']


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
