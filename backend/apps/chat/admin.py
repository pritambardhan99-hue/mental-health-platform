from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_by', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'created_by__id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'sender_type', 'message_preview', 'timestamp', 'is_flagged']
    list_filter = ['sender_type', 'is_flagged', 'timestamp']
    search_fields = ['message_text']
    readonly_fields = ['id', 'timestamp']

    def message_preview(self, obj):
        return obj.message_text[:60] + '...' if len(obj.message_text) > 60 else obj.message_text
    message_preview.short_description = 'Message'
