"""
Main URL Configuration
======================
This is the entry point for all API routes.
Each app has its own urls.py, and we include them here with a prefix.

API Structure:
  /api/auth/      → User registration, JWT token management
  /api/chat/      → Chat rooms and messages
  /api/mood/      → Mood tracking
  /api/emergency/ → Emergency detection
  /api/chatbot/   → AI chatbot
  /admin/         → Django admin panel
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin - useful for monitoring data
    path('admin/', admin.site.urls),

    # Authentication routes: register, login, token refresh
    path('api/auth/', include('apps.users.urls')),

    # Chat routes: create rooms, list messages
    path('api/chat/', include('apps.chat.urls')),

    # Mood tracking routes: submit mood, get history
    path('api/mood/', include('apps.mood.urls')),

    # Emergency routes: check keywords, get help resources
    path('api/emergency/', include('apps.emergency.urls')),

    # AI Chatbot routes: send message, get AI response
    path('api/chatbot/', include('apps.chatbot.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
