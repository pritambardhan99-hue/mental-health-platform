from django.urls import path
from .views import CheckEmergencyView, EmergencyResourcesView, EmergencyLogsView

urlpatterns = [
    path('check/', CheckEmergencyView.as_view(), name='check-emergency'),
    path('resources/', EmergencyResourcesView.as_view(), name='emergency-resources'),
    path('logs/', EmergencyLogsView.as_view(), name='emergency-logs'),
]
