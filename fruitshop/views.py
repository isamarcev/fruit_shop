import datetime

from django.core.cache import cache
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from fruitshop import models
from fruitshop.services import get_true_fruit_name, validate_integer
from users.models import Message

from django.contrib.auth.views import LoginView
from django.contrib.auth import login as auth_login, get_user_model
from django.contrib.auth import logout as auth_logout

from .tasks import task_check_warehouse


User = get_user_model()


def index(request, context=None):
    user_id = request.user.id
    progress_audit = cache.get(f'user_{user_id}_progress')
    procucts = models.Product.objects.all().prefetch_related('transaction_set')
    messages = Message.objects.all()[0:40][::-1]
    account = models.PersonalAccount.objects.first()
    declaration_count = models.Declaration.objects.filter(date__gte=datetime.date.today()).count()
    if context is None:
        context = dict()
    context['products'] = procucts
    context['messages'] = messages
    context['account'] = account
    context['declaration_count'] = declaration_count
    context['progress_audit'] = progress_audit
    return render(request, 'fruitsshop/index.html', context=context)


class Login(LoginView):
    success_url = reverse_lazy('start_page')

    def post(self, request, *args, **kwargs):
        user = request.POST.get('username')
        password = request.POST.get("password")
        if user and password:
            user_instance = User.objects.filter(username=user)
            if user_instance.exists():
                user_account = user_instance.first()
                checker_password = user_account.check_password(password)
                if checker_password:
                    auth_login(request, user=user_account)
                    return HttpResponseRedirect(self.success_url)
            else:
                return index(request, context={'error_login': 'Вы ввели неправильный логин или пароль. '
                                                          'Проверьте данные и попробуйте еще раз'})
        return index(request, context={'error_login': 'Все поля авторизации обязательный к заполнению!'})


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse_lazy('start_page'))


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
        models.Declaration.objects.create(file=file, account=account)
        declaration_count = models.Declaration.objects.filter(date__gte=datetime.date.today()).count()
        return JsonResponse({"success": declaration_count})
    else:
        return JsonResponse({"error": "Чтобы добавить декларацию авторизуйтесь в системе"})


def start_audit(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        if cache.get(f'user_{user_id}') is None:
            cache.set(f'user_{user_id}', 1)
            task_check_warehouse.delay(user_id)
            return JsonResponse({}, status=200)
        return JsonResponse({}, status=400)
