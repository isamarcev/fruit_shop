from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from fruitshop import models
from fruitshop.services import get_true_fruit_name
from users.models import Message
# Create your views here.


def index(request):
    procucts = models.Product.objects.all().prefetch_related('transaction_set')
    messages = Message.objects.all()[0:40][::-1]
    account = models.PersonalAccount.objects.first()
    return render(request, 'fruitsshop/index.html', context={"products": procucts,
                                                             "messages": messages,
                                                             "account": account})


def ajax_last_transactions(request):
    if request.is_ajax() and request.method == "GET":
        fruits = models.Product.objects.all().prefetch_related('transaction_set')
        data = {}
        for fruit in fruits:
            last_transaction = fruit.transaction_set.last()
            operation_type = "продано" if last_transaction.type == "Продажа" else "куплено"
            data[fruit.id] = f'{last_transaction.date.strftime("%d.%m.%Y, %H:%M")} - {operation_type} ' \
                             f'{last_transaction.count} {get_true_fruit_name(fruit.name, last_transaction.count)} ' \
                             f'за {last_transaction.sum} USD'
        return JsonResponse({'data': data})
    else:
        return HttpResponse("Only AJAX request")
