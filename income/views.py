from django.shortcuts import render, redirect
from .models import Income, Source
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import datetime
import calendar
import json
import os


@login_required(login_url='/authentication/login')
def search_income(request):
    data = request.body.decode('utf-8')
    search_val = json.loads(data).get('data')
    income = Income.objects.filter(name__icontains=search_val, owner=request.user) | Income.objects.filter(
        amount__startswith=search_val, owner=request.user) | Income.objects.filter(
        date__icontains=search_val, owner=request.user) | Income.objects.filter(
        category__icontains=search_val, owner=request.user)
    data = list(income.values())
    return JsonResponse(data, safe=False)


@login_required(login_url='/authentication/login')
def income(request):
    sources = Source.objects.all()
    income = Income.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)  # Show 7 items per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'sources': sources,
        'income': income,
        'page_obj': page_obj,
    }
    return render(request=request, template_name='income/index.html', context=context)


@login_required(login_url='/authentication/login')
def income_add(request):
    sources = Source.objects.all()
    file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(file, 'currencies.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        json_file.close()
    sources = Source.objects.all()
    arr = []
    for key, value in data.items():
        arr.append({'name': key, 'value': value})
    if request.method == 'GET':
        context = {
            'currencies': arr,
            'sources': sources}
        return render(request=request, template_name='income/new.html', context=context)
    context = {
        'values': request.POST,
        'sources': sources,
        'currencies': arr,
    }
    amount = request.POST['amount']
    description = request.POST['name']
    currency = request.POST['currency']

    date = request.POST['date']
    source = request.POST['source']
    if not amount:
        messages.error(request,  'Amount is required')
        return render(request=request, template_name='income/new.html', context=context)
    if not source:
        messages.error(request,  'Income Source is required')
        return render(request=request, template_name='income/new.html', context=context)
    income = Income.objects.create(
        amount=amount, description=description, source=source, currency=currency, date=date, owner=request.user)

    if income:
        messages.success(request,  'Income was submitted successfully')
        return redirect('income')

    return render(request=request, template_name='income/index.html')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    data = []
    arr = []
    file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(file, 'currencies.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        json_file.close()
    sources = Source.objects.all()
    arr = []
    for key, value in data.items():
        arr.append({'name': key, 'value': value})

    context = {
        'values': request.POST,
        'sources': sources,
        'income': income
    }
    if request.method == 'GET':
        return render(request, 'income/edit.html', context)
    amount = request.POST['amount']
    category = request.POST['category']
    currency = request.POST['currency']
    name = request.POST['name']
    if not amount:
        messages.error(request,  'Amount is required')
        return redirect('income')
    if not name:
        messages.error(request,  'Reason for the request is required')
        return redirect('income')
    income.amount = amount
    income.name = name
    income.currency = currency
    income.category = category
    income.save()
    messages.success(request,  'Income updated successfully')
    return redirect('income')


@login_required(login_url='/authentication/login')
def income_delete(request):
    income = Income.objects.all_income()
    context = {
        'income': income
    }
    return render('income/index.html', context)


@login_required(login_url='/authentication/login')
def income_summary(request):
    all_income = Income.objects.all()
    today = datetime.datetime.today().date()
    today2 = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    month_ago = today - datetime.timedelta(days=30)
    year_ago = today - datetime.timedelta(days=366)
    todays_amount = 0
    todays_count = 0
    this_week_amount = 0
    this_week_count = 0
    this_month_amount = 0
    this_month_count = 0
    this_year_amount = 0
    this_year_count = 0

    for one in all_income:
        if one.date == today:
            todays_amount += one.amount
            todays_count += 1

        if one.date >= week_ago:
            this_week_amount += one.amount
            this_week_count += 1

        if one.date >= month_ago:
            this_month_amount += one.amount
            this_month_count += 1

        if one.date >= year_ago:
            this_year_amount += one.amount
            this_year_count += 1

    context = {
        'today': {
            'amount': todays_amount,
            "count": todays_count,

        },
        'this_week': {
            'amount': this_week_amount,
            "count": this_week_count,

        },
        'this_month': {
            'amount': this_month_amount,
            "count": this_month_count,

        },
        'this_year': {
            'amount': this_year_amount,
            "count": this_year_count,

        },

    }
    return render(request, 'income/summary.html', context)


def income_summary_rest(request):
    all_income = Income.objects.all()
    today = datetime.datetime.today().date()
    today_amount = 0
    months_data = {}
    week_days_data = {}

    def get_amount_for_month(month):
        month_amount = 0
        for one in all_income:
            month_, year = one.date.month, one.date.year
            if month == month_ and year == today_year:
                month_amount += one.amount
        return month_amount

    for x in range(1, 13):
        today_month, today_year = x, datetime.datetime.today().year
        for one in all_income:
            months_data[x] = get_amount_for_month(x)

    def get_amount_for_day(x, today_day, month, today_year):
        day_amount = 0
        for one in all_income:
            day_, date_,  month_, year_ = one.date.isoweekday(
            ), one.date.day, one.date.month, one.date.year
            if x == day_ and month == month_ and year_ == today_year:
                if not day_ > today_day:
                    day_amount += one.amount
        return day_amount

    for x in range(1, 8):
        today_day, today_month, today_year = datetime.datetime.today(
        ).isoweekday(), datetime.datetime.today(
        ).month, datetime.datetime.today().year
        for one in all_income:
            week_days_data[x] = get_amount_for_day(
                x, today_day, today_month, today_year)

    data = {"months": months_data, "days": week_days_data}
    return JsonResponse({'data': data}, safe=False)


@login_required(login_url='/authentication/login')
def income_detail(request):
    income = Income.objects.all_income()
    context = {
        'income': income
    }
    return render('income/index.html', context)


@login_required(login_url='/authentication/login')
def income_delete(request, id):
    Income.objects.get(id=id).delete()
    messages.success(request, 'Income  Deleted')
    return redirect('income')
