"""
Emergency Views
===============
REST API endpoints for the emergency detection system.

ENDPOINTS:
  POST /api/emergency/check/     → Check text for keywords (frontend call)
  GET  /api/emergency/resources/ → Get helpline resources
  GET  /api/emergency/logs/      → Get user's emergency log history
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import EmergencyLog
from .utils import detect_emergency_keywords, get_severity, HELPLINE_RESOURCES


class CheckEmergencyView(APIView):
    """
    POST /api/emergency/check/
    
    Checks a piece of text for emergency keywords.
    Used by the frontend to check mood notes before submitting.
    
    Request Body:
    {
        "text": "I feel so hopeless and want to end it all",
        "source": "mood_note"  // optional: 'chat', 'chatbot', 'mood_note'
    }
    
    Response:
    {
        "is_emergency": true,
        "severity": "high",
        "keywords_found": ["hopeless", "end it all"],
        "resources": [...]
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = request.data.get('text', '').strip()
        source = request.data.get('source', 'chat')

        if not text:
            return Response(
                {'error': 'Text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_emergency, keywords_found = detect_emergency_keywords(text)

        if is_emergency:
            severity = get_severity(keywords_found)

            # Log to database
            EmergencyLog.objects.create(
                user=request.user,
                detected_text=text,
                keywords_found=keywords_found,
                severity=severity,
                source=source,
                alert_triggered=True
            )

            return Response({
                'is_emergency': True,
                'severity': severity,
                'keywords_found': keywords_found,
                'resources': HELPLINE_RESOURCES,
                'message': 'We noticed some concerning words. Help is available.',
            })

        return Response({
            'is_emergency': False,
            'severity': 'none',
            'keywords_found': [],
            'resources': [],
        })


class EmergencyResourcesView(APIView):
    """
    GET /api/emergency/resources/
    
    Returns list of mental health helpline resources.
    No authentication required — anyone in crisis should see these.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'resources': HELPLINE_RESOURCES,
            'message': 'You are not alone. Help is available 24/7.'
        })


class EmergencyLogsView(APIView):
    """
    GET /api/emergency/logs/
    
    Returns current user's emergency log history.
    Useful for user to review their history.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = EmergencyLog.objects.filter(user=request.user)[:20]
        data = [{
            'id': log.id,
            'severity': log.severity,
            'keywords_found': log.keywords_found,
            'source': log.source,
            'timestamp': log.timestamp.isoformat(),
        } for log in logs]
        return Response({'logs': data, 'total': len(data)})
