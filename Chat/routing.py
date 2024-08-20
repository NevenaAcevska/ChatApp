# Chat/routing.py

from django.urls import re_path
from Chat import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]
