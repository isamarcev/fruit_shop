import datetime
import json

from . import models
from users.models import Message

from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("CONNETCT")
        print(self.scope['user'])

        print(self.scope)
        await self.accept()

    async def disconnect(self, close_code):
        # await self.disconnect()
        pass

    async def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")
        if message:
            new_message = await self.create_message(message, self.scope.get("user"))
            await self.send(text_data=json.dumps({"message": new_message.text, "time": new_message.date.strftime("%H:%M") }))

        # await self.send(text_data=json.dumps({"message": message}))

    async def chat_message(self, event):
        print(event, 'veve')
        message = event['message']
        await self.send(text_data=json.dumps({"message": message, "time": datetime.time.strftime("%H:%M")}))


    @database_sync_to_async
    def create_message(self, message, user):
        new_message = Message.objects.create(
            user=user,
            text=message
        )
        return new_message
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