from django.shortcuts import render, redirect
from .models import Expense, Category
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


def index(request):
    return redirect('expenses')


@login_required(login_url='/authentication/login')
def search_expenses(request):
    search_val = json.loads(request.body).get('data')
    expenses = Expense.objects.filter(name__icontains=search_val, owner=request.user) | Expense.objects.filter(
        amount__startswith=search_val, owner=request.user) | Expense.objects.filter(
        date__icontains=search_val, owner=request.user) | Expense.objects.filter(
        category__icontains=search_val, owner=request.user)
    data = list(expenses.values())
    return JsonResponse(data, safe=False)


@login_required(login_url='/authentication/login')
def expenses(request):

    if not Setting.objects.filter(user=request.user).exists():
        messages.info(request, 'Please choose your preferred currency')
        return redirect('general-settings')
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency = Setting.objects.get(user=request.user).currency
    context = {
        'currency': currency.split('-')[0],
        'categories': categories,
        'expenses': expenses,
        'page_obj': page_obj,
    }
    return render(request=request, template_name='expenses/index.html', context=context)


@login_required(login_url='/authentication/login')
def expenses_add(request):
    categories = Category.objects.all()

    if not Setting.objects.filter(user=request.user).exists():
        messages.info(request, 'Please choose your preferred currency')

        return redirect('general-settings')

    if request.method == 'GET':
        context = {
            'categories': categories,
            'settings': Setting.objects.filter(user=request.user)[0] if Setting.objects.filter(user=request.user).exists() else {}
        }
        return render(request=request, template_name='expenses/new.html', context=context)
    context = {
        'values': request.POST,
        'categories': categories,
    }
    amount = request.POST['amount']
    name = request.POST['name']
    category = request.POST['category']
    date = request.POST['ex_date']
    if not amount:
        messages.error(request,  'Amount is required')
        return render(request=request, template_name='expenses/new.html', context=context)

    if not date:
        messages.error(request,  'Date is required')
        return render(request=request, template_name='expenses/new.html', context=context)
    if not category:
        messages.error(request,  'Expense Category is required')
        return render(request=request, template_name='expenses/new.html', context=context)
    expense = Expense.objects.create(
        amount=amount, name=name, date=date, category=category, owner=request.user)

    if expense:
        messages.success(request,  'Expense was submitted successfully')
        return redirect('expenses')

    return render(request=request, template_name='expenses/index.html')


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    data = []
    arr = []

    file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(file, 'currencies.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        json_file.close()
    categories = Category.objects.all()
    context = {
        'values': request.POST,
        'categories': categories,
        'expense': expense
    }
    if request.method == 'GET':
        context = {
            'values': expense,
            'categories': categories,
            'expense': expense
        }
        return render(request, 'expenses/edit.html', context)
    amount = request.POST['amount']
    category = request.POST['category']
    name = request.POST['name']
    if not amount:
        messages.error(request,  'Amount is required')
        return render(request, 'expenses/edit.html', context)
    expense.amount = amount
    expense.name = name
    expense.category = category
    expense.save()
    messages.success(request,  'Expense updated successfully')
    return redirect('expenses')


@login_required(login_url='/authentication/login')
def expense_delete(request):
    expenses = Expense.objects.all_expenses()
    context = {
        'expenses': expenses
    }
    return render('expenses/index.html', context)


@login_required(login_url='/authentication/login')
def expense_summary(request):

    if not Setting.objects.filter(user=request.user).exists():
        messages.info(request, 'Please choose your preferred currency')
        return redirect('general-settings')
    all_expenses = Expense.objects.filter(owner=request.user)
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

    for one in all_expenses:
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

    currency = Setting.objects.get(user=request.user).currency
    context = {
        'currency': currency.split('-')[0],
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
    return render(request, 'expenses/summary.html', context)


def expense_summary_rest(request):
    all_expenses = Expense.objects.filter(owner=request.user,)
    today = datetime.datetime.today().date()
    today_amount = 0
    months_data = {}
    week_days_data = {}

    def get_amount_for_month(month):
        month_amount = 0
        for one in all_expenses:
            month_, year = one.date.month, one.date.year
            if month == month_ and year == today_year:
                month_amount += one.amount
        return month_amount

    for x in range(1, 13):
        today_month, today_year = x, datetime.datetime.today().year
        for one in all_expenses:
            months_data[x] = get_amount_for_month(x)

    def get_amount_for_day(x, today_day, month, today_year):
        day_amount = 0
        for one in all_expenses:
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
        for one in all_expenses:
            week_days_data[x] = get_amount_for_day(
                x, today_day, today_month, today_year)

    data = {"months": months_data, "days": week_days_data}
    return JsonResponse({'data': data}, safe=False)


def last_3months_stats(request):
    todays_date = datetime.date.today()
    three_months_ago = datetime.date.today() - datetime.timedelta(days=90)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=three_months_ago, date__lte=todays_date)

    # categories occuring.
    def get_categories(item):
        return item.category
    final = {}
    categories = list(set(map(get_categories, expenses)))

    def get_expense_count(y):
        new = Expense.objects.filter(category=y,)
        count = new.count()
        amount = 0
        for y in new:
            amount += y.amount
        return {'count': count, 'amount': amount}

    for x in expenses:
        for y in categories:
            final[y] = get_expense_count(y)
    return JsonResponse({'category_data': final}, safe=False)


@login_required(login_url='/authentication/login')
def expense_detail(request):
    expenses = Expense.objects.all_expenses()
    context = {
        'expenses': expenses
    }
    return render('expenses/index.html', context)


@login_required(login_url='/authentication/login')
def expense_delete(request, id):
    Expense.objects.get(id=id).delete()
    messages.success(request, 'Expense  Deleted')
    return redirect('expenses')


def last_3months_expense_source_stats(request):
    todays_date = datetime.date.today()
    last_month = datetime.date.today() - datetime.timedelta(days=0)
    last_2_month = last_month - datetime.timedelta(days=30)
    last_3_month = last_2_month - datetime.timedelta(days=30)

    last_month_income = Expense.objects.filter(owner=request.user,
                                               date__gte=last_month, date__lte=todays_date).order_by('date')
    prev_month_income = Expense.objects.filter(owner=request.user,
                                               date__gte=last_month, date__lte=last_2_month)
    prev_prev_month_income = Expense.objects.filter(owner=request.user,
                                                    date__gte=last_2_month, date__lte=last_3_month)

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
