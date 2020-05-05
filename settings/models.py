from django.db import models
from django.contrib.auth.models import User


class Setting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return str(self.user) + ' s'+' settings'
