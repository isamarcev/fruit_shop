import datetime
import json

from . import models
from users.models import Message, User

from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

from .tasks import task_buy_fruits


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
        if message:
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
        print(time)
        await self.send(text_data=json.dumps({"user": user, "message": message, "time": time}))

    @database_sync_to_async
    def create_message(self, message, user):
        user = User.objects.first()
        new_message = Message.objects.create(
            user=user,
            text=message
        )
        return new_message



class FruitConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'shop'
        self.room_group_name = "chat_%s" % self.room_name
        print("CONNECT")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        print("RECEIVE")
        text_data_json = json.loads(text_data)
        fruit = text_data_json.get("fruit_id")
        count = text_data_json.get("count")
        if fruit:
            task = task_buy_fruits.delay(fruit, count=int(count), auto=False)
            # result = task.get()
            # print(result)
            # new_message = await self.create_message(fruit, self.scope.get("user"))
            # time = new_message.date + datetime.timedelta(hours=2)
            # await self.channel_layer.group_send(
            #     self.room_group_name, {"type": "chat_buying",
            #                            "success": result.success,
                                       # "user": f'{new_message.user.username}',
                                       # "time": time.strftime("%H:%M")}
                                       # })

    async def chat_buying(self, event):
        success = event["success"]
        # user = event["user"]
        # time = event["time"]
        # print(time)
        await self.send(text_data=json.dumps({"success": success,
                                              # "message": message, "time": time
                                              }))

    # @database_sync_to_async
    # def create_message(self, message, user):
    #     user = User.objects.first()
    #     new_message = Message.objects.create(
    #         user=user,
    #         text=message
    #     )
    #     return new_message
# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#
#         self.accept()
#
#     def disconnect(self, close_code):
#         pass
#
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#
#         self.send(text_data=json.dumps({"message": message}))