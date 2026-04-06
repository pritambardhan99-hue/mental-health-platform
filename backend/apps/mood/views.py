"""
Mood Tracking Views
===================
API endpoints for submitting and retrieving mood data.

ENDPOINTS:
  POST /api/mood/log/           → Submit today's mood
  GET  /api/mood/history/       → Get mood history
  GET  /api/mood/stats/weekly/  → Weekly stats for chart
  GET  /api/mood/stats/monthly/ → Monthly stats for chart
  GET  /api/mood/today/         → Get today's mood entry
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg, Count
from collections import Counter
from datetime import timedelta

from .models import MoodEntry
from .serializers import MoodEntrySerializer, MoodStatsSerializer


class LogMoodView(APIView):
    """
    POST /api/mood/log/
    
    Submit or update today's mood.
    If user already submitted today, updates the existing entry (upsert).
    
    Request Body:
    {
        "mood": "happy",
        "note": "Had a good day, went for a walk"  ← optional
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        today = timezone.now().date()

        # Use update_or_create: update if exists, create if not
        # This prevents duplicate entries for the same day
        entry, created = MoodEntry.objects.update_or_create(
            user=request.user,
            date=today,
            defaults={
                'mood': request.data.get('mood'),
                'note': request.data.get('note', ''),
            }
        )

        serializer = MoodEntrySerializer(entry)
        return Response({
            'data': serializer.data,
            'is_new': created,
            'message': 'Mood logged!' if created else 'Mood updated for today!'
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class TodayMoodView(APIView):
    """
    GET /api/mood/today/
    Returns today's mood entry if it exists.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        try:
            entry = MoodEntry.objects.get(user=request.user, date=today)
            return Response(MoodEntrySerializer(entry).data)
        except MoodEntry.DoesNotExist:
            return Response(
                {'message': 'No mood logged today yet'},
                status=status.HTTP_404_NOT_FOUND
            )


class MoodHistoryView(APIView):
    """
    GET /api/mood/history/?days=30
    
    Returns mood entries for the past N days.
    Default: last 30 days.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        days = min(days, 365)  # Cap at 1 year

        start_date = timezone.now().date() - timedelta(days=days)
        entries = MoodEntry.objects.filter(
            user=request.user,
            date__gte=start_date
        ).order_by('date')  # Chronological for charting

        serializer = MoodEntrySerializer(entries, many=True)
        return Response({
            'period_days': days,
            'entries': serializer.data,
            'total': entries.count()
        })


class WeeklyStatsView(APIView):
    """
    GET /api/mood/stats/weekly/
    
    Returns mood statistics for the past 7 days.
    Used to render the weekly mood chart on the dashboard.
    
    Response includes:
    - entries: list of mood entries (one per day)
    - average_score: e.g., 3.5
    - most_common_mood: e.g., "calm"
    - mood_distribution: {"happy": 3, "sad": 1, ...}
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = timezone.now().date() - timedelta(days=7)
        entries = MoodEntry.objects.filter(
            user=request.user,
            date__gte=start_date
        ).order_by('date')

        return Response(self._build_stats(entries, 'weekly'))

    def _build_stats(self, entries, period):
        if not entries.exists():
            return {
                'period': period,
                'entries': [],
                'average_score': 0,
                'most_common_mood': None,
                'mood_distribution': {},
                'total_entries': 0
            }

        moods = [e.mood for e in entries]
        scores = [e.mood_score for e in entries]
        mood_count = Counter(moods)

        return {
            'period': period,
            'entries': MoodEntrySerializer(entries, many=True).data,
            'average_score': round(sum(scores) / len(scores), 2),
            'most_common_mood': mood_count.most_common(1)[0][0],
            'mood_distribution': dict(mood_count),
            'total_entries': len(moods)
        }


class MonthlyStatsView(WeeklyStatsView):
    """
    GET /api/mood/stats/monthly/
    Same as weekly but for last 30 days.
    """

    def get(self, request):
        start_date = timezone.now().date() - timedelta(days=30)
        entries = MoodEntry.objects.filter(
            user=request.user,
            date__gte=start_date
        ).order_by('date')

        return Response(self._build_stats(entries, 'monthly'))
