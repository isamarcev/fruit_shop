import datetime
import json

from .services import validate_integer
from users.models import Message, User

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .tasks import task_buy_fruits, task_sell_fruits


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat'
        self.room_group_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")
        if message and not message.isspace():
            new_message = await self.create_message(message, self.scope.get("user"))
            time = new_message.date + datetime.timedelta(hours=2)
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message",
                                       "message": new_message.text,
                                       "user": f'{new_message.user.username}',
                                       "time": time.strftime("%H:%M")}
            )

    async def chat_message(self, event):
        message = event["message"]
        user = event["user"]
        time = event["time"]
        await self.send(text_data=json.dumps({"user": user, "message": message, "time": time}))

    @database_sync_to_async
    def create_message(self, message, user):
        if not user.is_authenticated:
            user = User.objects.get(username="anonim")
        new_message = Message.objects.create(
            user=user,
            text=message
        )
        return new_message


class FruitConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'shop'
        self.room_group_name = "chat_%s" % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        if self.scope["user"].is_anonymous:
            await self.send(text_data=json.dumps({
                "error": "Для торговли вам необходимо авторизоваться в системе!"
            }))
        text_data_json = json.loads(text_data)
        fruit = validate_integer(text_data_json.get("fruit_id"))
        count = validate_integer(text_data_json.get("count"))
        if fruit and count:
            if text_data_json['action'] == 'buy':
                await sync_to_async(task_buy_fruits.apply_async)((fruit, count, False))
            elif text_data_json['action'] == 'sell':
                await sync_to_async(task_sell_fruits.apply_async)((fruit, count, False))
        else:
            await self.send(text_data=json.dumps({
                "error": "Количество должно быть введено цифрой!"
            }))

    async def chat_buying(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_selling(self, event):
        await self.send(text_data=json.dumps(event))


class AuditConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = f'audit_{self.scope["url_route"]["kwargs"]["id"]}'
        self.room_group_name = "chat_%s" % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def update_progress_bar(self, event):
        await self.send(text_data=json.dumps({
                "progress": event['progress']
            }))
