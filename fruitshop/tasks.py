import datetime
import random

from asgiref.sync import async_to_sync
from django_celery_beat.models import IntervalSchedule, PeriodicTask, PeriodicTasks
import httpx
from channels.layers import get_channel_layer
from config.celery import app

import translators.server as tss

from fruitshop import models


@app.on_after_finalize.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(10, task_jester.s(), name="joke")
    sender.add_periodic_task(10, task_buy_fruits.s(1), name="buy_pineapple")
    sender.add_periodic_task(10, task_buy_fruits.s(2), name="buy_apple")
    sender.add_periodic_task(10, task_buy_fruits.s(3), name="buy_banana")
    sender.add_periodic_task(10, task_buy_fruits.s(4), name="buy_orange")
    sender.add_periodic_task(10, task_buy_fruits.s(5), name="buy_apricot")
    sender.add_periodic_task(10, task_buy_fruits.s(6), name="buy_kiwi")


@app.task
def task_jester():
    from django.contrib.auth.models import User
    from users.models import Message

    channel_layer = get_channel_layer()
    jester = User.objects.get(username='admin')

    response = httpx.get('https://v2.jokeapi.dev/joke/Any?type=single')
    joke = response.json().get('joke')
    translated_joke = tss.bing(joke, from_language='en', to_language='ru')

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
    task = PeriodicTask.objects.get(task='fruitshop.tasks.task_jester')
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
        count = random.randint(1, 20)
    price = random.randint(1, 7)
    sum = count * price
    success = False
    print(type(sum))
    print(type(account.balance))
    operation = int(account.balance) - sum
    if operation >= 0:
        success = True
        fruit.balance = fruit.balance - count
        fruit.save()
        account.balance = operation
        account.save()
    transaction = models.Transaction.objects.create(type="Покупка",
                                                    product=fruit,
                                                    account=account,
                                                    count=count,
                                                    price=price,
                                                    success=success)
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        'chat_shop',
        {
            "type": "chat_buying",
            "success": transaction.success,
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
        task = PeriodicTask.objects.get(task='fruitshop.tasks.task_buy_fruits')
        task.interval = schedule
        task.save()
        PeriodicTasks.changed(task)
    # return transaction





