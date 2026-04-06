from django.contrib import admin
from .models import MoodEntry


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood', 'mood_score', 'date', 'created_at']
    list_filter = ['mood', 'date']
    search_fields = ['user__id', 'note']
    readonly_fields = ['created_at', 'updated_at', 'mood_score', 'mood_emoji']
    ordering = ['-date']
