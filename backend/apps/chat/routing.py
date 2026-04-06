"""
WebSocket URL Routing
=====================
Just like urls.py maps HTTP paths to views,
routing.py maps WebSocket paths to consumers.

URL Pattern: ws://localhost:8000/ws/chat/<room_id>/

The <room_id> is captured and passed to the consumer as:
  self.scope['url_route']['kwargs']['room_id']
"""

from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    # ws://domain/ws/chat/550e8400-e29b-41d4-a716-446655440000/
    re_path(r'ws/chat/(?P<room_id>[0-9a-f-]+)/$', ChatConsumer.as_asgi()),
]
