"""
Chat Serializers
================
Convert ChatRoom and Message model instances to/from JSON for REST API.
"""

from rest_framework import serializers
from .models import ChatRoom, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializes a single chat message."""
    sender_id = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'sender_type', 'message_text', 'timestamp', 'is_flagged']
        read_only_fields = ['id', 'sender_id', 'sender_type', 'timestamp', 'is_flagged']

    def get_sender_id(self, obj):
        return str(obj.sender.id) if obj.sender else None


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializes a chat room with its recent messages."""
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'created_at', 'updated_at', 'message_count', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class CreateRoomSerializer(serializers.ModelSerializer):
    """Used when creating a new chat room."""

    class Meta:
        model = ChatRoom
        fields = ['name']
