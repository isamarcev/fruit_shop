import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from fruitshop import models
from fruitshop.services import get_true_fruit_name, validate_integer
from users.models import Message
# Create your views here.


def index(request):
    procucts = models.Product.objects.all().prefetch_related('transaction_set')
    messages = Message.objects.all()[0:40][::-1]
    account = models.PersonalAccount.objects.first()
    declaration_count = models.Declaration.objects.filter(date__gte=datetime.date.today()).count()
    return render(request, 'fruitsshop/index.html', context={"products": procucts,
                                                             "messages": messages,
                                                             "account": account,
                                                             "declaration_count": declaration_count})


def ajax_last_transactions(request):
    if request.method == "GET":
        fruits = models.Product.objects.all().prefetch_related('transaction_set')
        data = {}
        for fruit in fruits:
            last_transaction = fruit.transaction_set.last()
            if last_transaction:
                operation_type = "продано" if last_transaction.type == "Продажа" else "куплено"
                data[fruit.id] = f'{(last_transaction.date + datetime.timedelta(hours=2)).strftime("%d.%m.%Y, %H:%M")} - {operation_type} ' \
                                 f'{last_transaction.count} {get_true_fruit_name(fruit.name, last_transaction.count)} ' \
                                 f'за {last_transaction.sum} USD'
        return JsonResponse(data)
    else:
        return HttpResponse("Only AJAX request")


def ajax_money_bank(request):
    if request.method == "GET":
        operation = request.GET.get("operation")
        value = request.GET.get("value")
        if not validate_integer(value):
            return JsonResponse({"error": "Напишите числовое значение"})
        account = models.PersonalAccount.objects.first()
        if operation == 'up':
            account.balance = account.balance + int(value)
            account.save()
            return JsonResponse({"success": 'Счет успешно пополнен!',
                                 'new_value': account.balance})
        elif operation == 'down':
            new_balance = account.balance - int(value)
            if new_balance >= 0:
                account.balance = new_balance
                account.save()
                return JsonResponse({"success": 'Деньги успешно выведены со счета',
                                     'new_value': account.balance})
            else:
                return JsonResponse({'error': 'Счет в банке не может быть меньше 0'})


def upload_declaration(request):
    if request.method == "POST" and request.user.is_authenticated:
        file = request.FILES.get("file")
        account = models.PersonalAccount.objects.first()
        declaration = models.Declaration.objects.create(file=file, account=account)
        declaration_count = models.Declaration.objects.filter(date__gte=datetime.date.today()).count()
        return JsonResponse({"success": declaration_count})
    else:
        return JsonResponse({"error": "Чтобы добавить декларацию авторизуйтесь в системе"})