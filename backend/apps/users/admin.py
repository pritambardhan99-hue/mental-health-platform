from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AnonymousUser


@admin.register(AnonymousUser)
class AnonymousUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'last_active', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['id']
    readonly_fields = ['id', 'created_at', 'last_active']
    ordering = ['-created_at']
