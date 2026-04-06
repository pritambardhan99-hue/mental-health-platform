"""
Chat Models
===========
DATABASE TABLES:
  chat_rooms    → Represents a conversation session
  messages      → Individual messages within a room

RELATIONSHIPS:
  ChatRoom ←→ AnonymousUser: A user can have many rooms (one-to-many via FK)
  Message → ChatRoom: Messages belong to a room (ForeignKey)
  Message → AnonymousUser: Messages have a sender (ForeignKey)

RELATIONSHIP DIAGRAM:
  AnonymousUser (1) ──── (many) ChatRoom
  ChatRoom (1) ──── (many) Message
  AnonymousUser (1) ──── (many) Message [sender]
"""

import uuid
from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    """
    Represents a chat session.
    
    Each user gets their own personal chat room for:
    1. Talking with the AI chatbot
    2. Anonymous peer support (future feature)
    
    WHY NOT JUST USE USER ID FOR CHAT?
    Rooms allow future multi-user chat, chat history isolation,
    and room-based WebSocket channels.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # The user who owns/created this room
    # on_delete=CASCADE: if user is deleted, their rooms are deleted too
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_rooms',
        help_text="The anonymous user who created this room"
    )

    # Human-readable name for the room
    name = models.CharField(
        max_length=100,
        default='My Safe Space',
        help_text="Name of the chat room"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-updated_at']  # Most recently active rooms first

    def __str__(self):
        return f"Room {str(self.id)[:8]} by {self.created_by}"


class Message(models.Model):
    """
    Individual messages within a chat room.
    
    SENDER TYPES:
    - 'user': Message from the anonymous human user
    - 'ai': Message from the AI chatbot
    - 'system': System notifications (e.g., "Emergency resources sent")
    
    NOTE: We store AI messages here too so we can display full conversation history.
    """

    SENDER_CHOICES = [
        ('user', 'User'),    # Human user message
        ('ai', 'AI'),         # AI chatbot response
        ('system', 'System'), # System notification
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Which room this message belongs to
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="The chat room this message is in"
    )

    # Who sent this message (null for AI/system messages)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Don't delete messages if user account deleted
        null=True,
        blank=True,
        related_name='sent_messages',
        help_text="The anonymous user who sent this (null for AI messages)"
    )

    # Whether this was sent by user, AI, or system
    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES,
        default='user'
    )

    # The actual message content
    message_text = models.TextField(
        help_text="The message content"
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    # Whether this message contained emergency keywords
    is_flagged = models.BooleanField(
        default=False,
        help_text="True if message contained emergency keywords"
    )

    class Meta:
        db_table = 'messages'
        ordering = ['timestamp']  # Oldest first (chronological chat order)

    def __str__(self):
        preview = self.message_text[:50]  # First 50 chars
        return f"[{self.sender_type}] {preview}..."
