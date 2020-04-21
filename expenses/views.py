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


def index(request):
    return redirect('expenses')


@login_required(login_url='/authentication/login')
def search_expenses(request):
    data = request.body.decode('utf-8')
    search_val = json.loads(data).get('data')
    expenses = Expense.objects.filter(name__icontains=search_val, owner=request.user) | Expense.objects.filter(
        amount__startswith=search_val, owner=request.user) | Expense.objects.filter(
        date__icontains=search_val, owner=request.user) | Expense.objects.filter(
        category__icontains=search_val, owner=request.user)
    data = list(expenses.values())
    return JsonResponse(data, safe=False)


@login_required(login_url='/authentication/login')
def expenses(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)  # Show 7 items per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'categories': categories,
        'expenses': expenses,
        'page_obj': page_obj,
    }
    return render(request=request, template_name='expenses/index.html', context=context)


@login_required(login_url='/authentication/login')
def expenses_add(request):
    data = []
    file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(file, 'currencies.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        json_file.close()
    categories = Category.objects.all()
    arr = []
    for key, value in data.items():
        arr.append({'name': key, 'value': value})
    if request.method == 'GET':
        context = {
            'categories': categories,
            'currencies': arr
        }
        return render(request=request, template_name='expenses/new.html', context=context)
    context = {
        'values': request.POST,
        'currencies': arr,
        'categories': categories,
    }
    amount = request.POST['amount']
    name = request.POST['name']
    currency = request.POST['currency']
    category = request.POST['category']
    date = request.POST['date']
    if not amount:
        messages.error(request,  'Amount is required')
        return render(request=request, template_name='expenses/new.html', context=context)
    if not category:
        messages.error(request,  'Expense Category is required')
        return render(request=request, template_name='expenses/new.html', context=context)
    expense = Expense.objects.create(
        amount=amount, name=name, currency=currency, date=date, category=category, owner=request.user)

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
    arr = []
    for key, value in data.items():
        arr.append({'name': key, 'value': value})

    context = {
        'values': request.POST,
        'currencies': arr,
        'categories': categories,
        'expense': expense
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit.html', context)
    amount = request.POST['amount']
    category = request.POST['category']
    print(category)
    currency = request.POST['currency']
    name = request.POST['name']
    if not amount:
        messages.error(request,  'Amount is required')
        return redirect('expenses')
    if not name:
        messages.error(request,  'Reason for the request is required')
        return redirect('expenses')
    expense.amount = amount
    expense.name = name
    expense.currency = currency
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
    all_expenses = Expense.objects.all()
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
    return render(request, 'expenses/summary.html', context)


def expense_summary_rest(request):
    all_expenses = Expense.objects.all()
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
    expenses = Expense.objects.filter(
        date__gte=three_months_ago, date__lte=todays_date)

    # categories occuring.
    def get_categories(item):
        return item.category
    final = {}
    categories = list(set(map(get_categories, expenses)))

    def get_expense_count(y):
        new = Expense.objects.filter(category=y)
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
