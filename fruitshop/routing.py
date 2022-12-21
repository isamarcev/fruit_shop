from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat/", consumers.ChatConsumer.as_asgi()),
    path("ws/fruit/", consumers.FruitConsumer.as_asgi()),
    path("ws/audit/<int:id>/", consumers.AuditConsumer.as_asgi()),
]