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
from settings.models import Setting


@login_required(login_url='/authentication/login')
def search_income(request):
    data = request.body.decode('utf-8')
    search_val = json.loads(data).get('data')
    income = Income.objects.filter(description__icontains=search_val, owner=request.user) | Income.objects.filter(
        amount__startswith=search_val, owner=request.user) | Income.objects.filter(
        date__icontains=search_val, owner=request.user) | Income.objects.filter(
        source__icontains=search_val, owner=request.user)
    data = list(income.values())
    return JsonResponse(data, safe=False)


@login_required(login_url='/authentication/login')
def income(request):
    if not Setting.objects.filter(user=request.user).exists():
        messages.info(request, 'Please choose your preferred currency')
        return redirect('general-settings')
    sources = Source.objects.all()
    income = Income.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)  # Show 7 items per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'currency': Setting.objects.get(user=request.user).currency.split('-')[0],
        'sources': sources,
        'income': income,
        'page_obj': page_obj,
    }
    return render(request=request, template_name='income/index.html', context=context)


@login_required(login_url='/authentication/login')
def income_add(request):
    sources = Source.objects.all()
    if request.method == 'GET':
        context = {
            'settings': Setting.objects.get(user=request.user),
            'sources': sources}
        return render(request=request, template_name='income/new.html', context=context)
    context = {
        'values': request.POST,
        'sources': sources,
    }
    amount = request.POST['amount']
    description = request.POST['description']

    income_date = request.POST['ex_date']
    source = request.POST['source']

    if not amount:
        messages.error(request,  'Amount is required')
        return render(request=request, template_name='income/new.html', context=context)
    if not source:
        messages.error(request,  'Income Source is required')
        return render(request=request, template_name='income/new.html', context=context)

    if not date:
        messages.error(request,  'Date is required')
        return render(request=request, template_name='income/new.html', context=context)

    income = Income.objects.create(
        amount=amount, description=description, source=source, date=date, owner=request.user)

    if income:
        messages.success(request,  'Income was submitted successfully')
        return redirect('income')

    return render(request=request, template_name='income/index.html')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'values': request.POST,
        'sources': sources,
        'income': income,
    }
    if request.method == 'GET':
        return render(request, 'income/edit.html', context)
    amount = request.POST['amount']
    description = request.POST['description']
    source = request.POST['source']
    name = request.POST['description']
    date = request.POST['ex_date']
    if not source:
        messages.error(request,  'source is required')
        return render(request, 'income/edit.html', context)
    if not amount:
        messages.error(request,  'Amount is required')
        return render(request, 'income/edit.html', context)
    income.amount = amount
    income.description = name
    income.description = description
    income.source = source
    income.income_date = date
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

    if not Setting.objects.filter(user=request.user).exists():
        messages.info(request, 'Please choose your preferred currency')
        return redirect('general-settings')
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
        if one.income_date == today:
            todays_amount += one.amount
            todays_count += 1

        if one.income_date >= week_ago:
            this_week_amount += one.amount
            this_week_count += 1

        if one.income_date >= month_ago:
            this_month_amount += one.amount
            this_month_count += 1

        if one.income_date >= year_ago:
            this_year_amount += one.amount
            this_year_count += 1

    context = {
        'currency': Setting.objects.get(user=request.user).currency.split('-')[0],
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
    all_income = Income.objects.filter(owner=request.user)
    today = datetime.datetime.today().date()
    today_amount = 0
    months_data = {}
    week_days_data = {}

    def get_amount_for_month(month):
        month_amount = 0
        for one in all_income:
            month_, year = one.income_date.month, one.income_date.year
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
            day_, date_,  month_, year_ = one.income_date.isoweekday(
            ), one.income_date.day, one.income_date.month, one.income_date.year
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


def last_3months_income_stats(request):
    todays_date = datetime.date.today()
    three_months_ago = datetime.date.today() - datetime.timedelta(days=90)
    income = Income.objects.filter(owner=request.user,
                                   income_date__gte=three_months_ago, income_date__lte=todays_date)
    # sources occuring.

    def get_sources(item):
        return item.source
    final = {}
    sources = list(set(map(get_sources, income)))

    def get_sources_count(y):
        new = Income.objects.filter(source=y)
        count = new.count()
        amount = 0
        for y in new:
            amount += y.amount
        return {'count': count, 'amount': amount}

    for x in income:
        for y in sources:
            final[y] = get_sources_count(y)
    return JsonResponse({'sources_data': final}, safe=False)


def last_3months_income_source_stats(request):
    todays_date = datetime.date.today()
    last_month = datetime.date.today() - datetime.timedelta(days=0)
    last_2_month = last_month - datetime.timedelta(days=30)
    last_3_month = last_2_month - datetime.timedelta(days=30)

    last_month_income = Income.objects.filter(owner=request.user,
                                              income_date__gte=last_month, income_date__lte=todays_date).order_by('income_date')
    prev_month_income = Income.objects.filter(owner=request.user,
                                              income_date__gte=last_month, income_date__lte=last_2_month)
    prev_prev_month_income = Income.objects.filter(owner=request.user,
                                                   income_date__gte=last_2_month, income_date__lte=last_3_month)

    keyed_data = []
    this_month_data = {'7th': 0, '15th': 0, '22nd': 0, '29th': 0}
    prev_month_data = {'7th': 0, '15th': 0, '22nd': 0, '29th': 0}
    prev_prev_month_data = {'7th': 0, '15th': 0, '22nd': 0, '29th': 0}

    for x in last_month_income:
        month = str(x.date)[:7]
        date_in_month = str(x.date)[:2]
        if int(date_in_month) <= 7:
            this_month_data['7th'] += x.amount
        if int(date_in_month) > 7 and int(date_in_month) <= 15:
            this_month_data['15th'] += x.amount
        if int(date_in_month) >= 16 and int(date_in_month) <= 21:
            this_month_data['22nd'] += x.amount
        if int(date_in_month) > 22 and int(date_in_month) < 31:
            this_month_data['29th'] += x.amount

    keyed_data.append({str(last_month): this_month_data})

    for x in prev_month_income:
        date_in_month = str(x.date)[:2]
        month = str(x.date)[:7]
        if int(date_in_month) <= 7:
            prev_month_data['7th'] += x.amount
        if int(date_in_month) > 7 and int(date_in_month) <= 15:
            prev_month_data['15th'] += x.amount
        if int(date_in_month) >= 16 and int(date_in_month) <= 21:
            prev_month_data['22nd'] += x.amount
        if int(date_in_month) > 22 and int(date_in_month) < 31:
            prev_month_data['29th'] += x.amount

    keyed_data.append({str(last_2_month): prev_month_data})

    for x in prev_prev_month_income:
        date_in_month = str(x.date)[:2]
        month = str(x.date)[:7]
        if int(date_in_month) <= 7:
            prev_prev_month_data['7th'] += x.amount
        if int(date_in_month) > 7 and int(date_in_month) <= 15:
            prev_prev_month_data['15th'] += x.amount
        if int(date_in_month) >= 16 and int(date_in_month) <= 21:
            prev_prev_month_data['22nd'] += x.amount
        if int(date_in_month) > 22 and int(date_in_month) < 31:
            prev_prev_month_data['29th'] += x.amount

    keyed_data.append({str(last_3_month): prev_month_data})
    return JsonResponse({'cumulative_income_data': keyed_data}, safe=False)
