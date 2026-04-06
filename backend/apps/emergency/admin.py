from django.contrib import admin
from .models import EmergencyLog


@admin.register(EmergencyLog)
class EmergencyLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'severity', 'source', 'alert_triggered', 'timestamp']
    list_filter = ['severity', 'source', 'alert_triggered', 'timestamp']
    readonly_fields = ['user', 'detected_text', 'keywords_found',
                       'severity', 'source', 'alert_triggered', 'timestamp']
    ordering = ['-timestamp']
    # Hide full text in list to protect privacy
    def get_queryset(self, request):
        return super().get_queryset(request)
