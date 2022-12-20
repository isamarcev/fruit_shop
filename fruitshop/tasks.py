import datetime
import random
from .services import get_true_fruit_name

from asgiref.sync import async_to_sync
from django_celery_beat.models import IntervalSchedule, PeriodicTask, PeriodicTasks
import httpx
from channels.layers import get_channel_layer
from config.celery import app

# import translators.server as tss

from fruitshop import models


@app.on_after_finalize.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(5, task_joker.s(), name="joke")
    sender.add_periodic_task(6, task_buy_fruits.s(1), name="buy_pineapple")
    sender.add_periodic_task(7, task_buy_fruits.s(2), name="buy_apple")
    sender.add_periodic_task(10, task_buy_fruits.s(3), name="buy_banana")
    sender.add_periodic_task(11, task_buy_fruits.s(4), name="buy_orange")
    sender.add_periodic_task(9, task_buy_fruits.s(5), name="buy_apricot")
    sender.add_periodic_task(8, task_buy_fruits.s(6), name="buy_kiwi")
    sender.add_periodic_task(10, task_sell_fruits.s(1), name="sell_pineapple")
    sender.add_periodic_task(10, task_sell_fruits.s(2), name="sell_apple")
    sender.add_periodic_task(10, task_sell_fruits.s(3), name="sell_banana")
    sender.add_periodic_task(10, task_sell_fruits.s(4), name="sell_orange")
    sender.add_periodic_task(10, task_sell_fruits.s(5), name="sell_apricot")
    sender.add_periodic_task(10, task_sell_fruits.s(6), name="sell_kiwi")


@app.task
def task_joker():
    from django.contrib.auth.models import User
    from users.models import Message

    channel_layer = get_channel_layer()
    jester = User.objects.get(username='admin')

    response = httpx.get('https://v2.jokeapi.dev/joke/Any?type=single')
    joke = response.json().get('joke')
    # translated_joke = tss.bing(joke, from_language='en', to_language='ru')
    translated_joke = joke
    joke_message = Message.objects.create(user=jester, text=translated_joke)
    date_time = joke_message.date + datetime.timedelta(hours=2)
    async_to_sync(channel_layer.group_send)(
        'chat_chat',
        {
            "type": "chat_message",
            "user": jester.username,
            "message": joke_message.text,
            "time": date_time.strftime("%H:%M")
        }
    )

    schedule, created = IntervalSchedule.objects.get_or_create(
        every=len(translated_joke),
        period=IntervalSchedule.SECONDS,
    )
    task = PeriodicTask.objects.get(task='fruitshop.tasks.task_joker')
    task.interval = schedule
    task.save()
    PeriodicTasks.changed(task)

    return joke


@app.task
def task_buy_fruits(fruit_id, count=None, auto=True):
    account = models.PersonalAccount.objects.first()
    fruit = models.Product.objects.get(pk=fruit_id)
    if count:
        count = count
    else:
        count = random.randint(1, 10)
    price = random.randint(3, 5)
    sum = count * price
    operation = int(account.balance) - sum

    transaction = models.Transaction.objects.create(type="Покупка",
                                                    product=fruit,
                                                    account=account,
                                                    count=count,
                                                    price=price,
                                                    success=True if operation >=0 else False,
                                                    auto_task=True if auto else False)
    if operation >= 0:
        fruit.balance = fruit.balance + count
        if not auto:
            fruit.last_operation = transaction
        fruit.save()
        account.balance = operation
        account.save()

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        'chat_shop',
        {
            "type": "chat_buying",
            "success": transaction.success,
            "balance_account": operation,
            "date_time": datetime.datetime.now().strftime("%d.%m.%Y, %H:%M"),
            "sum_operation": transaction.sum,
            "fruit": get_true_fruit_name(fruit.name, count),
            "fruit_id": fruit.id,
            "fruit_balance": fruit.balance,
            "count": count,
            "auto_task": transaction.auto_task
        }
    )
    if auto:
        random_time = random.randint(5, 20)
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=random_time,
            period=IntervalSchedule.SECONDS,
        )
        fruit_name = f'buy_{get_true_fruit_name(fruit.name, "english")}'
        task = PeriodicTask.objects.get(task='fruitshop.tasks.task_buy_fruits', name=fruit_name)
        task.interval = schedule
        task.save()
        PeriodicTasks.changed(task)


@app.task
def task_sell_fruits(fruit_id, count=None, auto=True):
    account = models.PersonalAccount.objects.first()
    fruit = models.Product.objects.get(pk=fruit_id)
    if count:
        count = count
    else:
        count = random.randint(4, 10)
    price = random.randint(4, 8)
    sum = count * price
    balance_fruit_after_sell = fruit.balance - count
    operation = int(account.balance) + sum

    transaction = models.Transaction.objects.create(type="Продажа",
                                                    product=fruit,
                                                    account=account,
                                                    count=count,
                                                    price=price,
                                                    success=True if balance_fruit_after_sell >= 0 else False,
                                                    auto_task=True if auto else False)
    if balance_fruit_after_sell >= 0:
        fruit.balance = balance_fruit_after_sell
        if not auto:
            fruit.last_operation = transaction
        fruit.save()
        account.balance = operation
        account.save()

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        'chat_shop',
        {
            "type": "chat_selling",
            "success": transaction.success,
            "balance_account": operation,
            "date_time": datetime.datetime.now().strftime("%d.%m.%Y, %H:%M"),
            "sum_operation": transaction.sum,
            "fruit": get_true_fruit_name(fruit.name, count),
            "fruit_id": fruit.id,
            "fruit_balance": fruit.balance,
            "count": count,
            "auto_task": transaction.auto_task

            # "message": joke_message.text,
            # "time": date_time.strftime("%H:%M")
        }
    )
    if auto:
        random_time = random.randint(5, 20)
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=random_time,
            period=IntervalSchedule.SECONDS,
        )
        fruit_name = f'sell_{get_true_fruit_name(fruit.name, "english")}'
        task = PeriodicTask.objects.get(task='fruitshop.tasks.task_sell_fruits', name=fruit_name)
        task.interval = schedule
        task.save()
        PeriodicTasks.changed(task)





