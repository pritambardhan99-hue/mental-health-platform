"""
ASGI Configuration
==================
ASGI (Asynchronous Server Gateway Interface) replaces WSGI when using Django Channels.
This file tells Django how to route incoming connections:
  - HTTP requests → Django views (normal REST API)
  - WebSocket connections → Django Channels consumers (real-time chat)
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mental_health_project.settings')
django.setup()

# Import WebSocket URL patterns AFTER django.setup()
from apps.chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # Regular HTTP requests → handled by Django normally
    'http': get_asgi_application(),

    # WebSocket connections → routed through our custom middleware and consumers
    # AuthMiddlewareStack: reads JWT from WebSocket headers and authenticates user
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Defined in apps/chat/routing.py
        )
    ),
})
