from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import User


class Income(models.Model):
    INCOME_SOURCE_OPTIONS = [
        ('SALARY', 'SALARY'),
        ('BUSINESS', 'BUSINESS'),
        ('SIDE_HUSLES', 'SIDE_HUSLES'),
        ('OTHERS', 'OTHERS')
    ]
    amount = models.FloatField(blank=False, null=False)
    currency = models.CharField(max_length=20, default="USD")
    created_at = models.DateTimeField(auto_now=True)
    description = models.TextField(default='_')
    date = models.DateField(default=now)
    source = models.CharField(
        max_length=200, choices=INCOME_SOURCE_OPTIONS, null=False, blank=False)
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.amount)

    class Meta:
        ordering = ['-created_at']


class Source(models.Model):
    name = models.CharField(max_length=20, default="SALARY")

    def __str__(self):
        return self.name
