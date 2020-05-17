from django.shortcuts import render
import json
import os
from .models import Setting
from django.contrib import messages
from django.conf import settings
# Create your views here.


def index(request):
    user_settings = Setting.objects.filter(user=request.user)[
        0] if Setting.objects.filter(user=request.user).exists() else None
    data = []
    file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        arr = []
        for key, value in data.items():
            arr.append({'name': key, 'value': value})
    if request.method == 'GET':
        return render(request, 'settings/index.html', context={'currencies': arr, 'settings': user_settings})
    else:
        currency = request.POST['currency']
        if user_settings is not None:
            user_settings.currency = currency
            user_settings.save()
        else:
            Setting.objects.create(user=request.user, currency=currency)
            user_settings['currency'] = currency
        messages.success(request, 'Changes saved successfully')

        return render(request, 'settings/index.html', context={'currencies': arr, 'settings': user_settings})


def account(request):
    return render(request, 'settings/account.html')
