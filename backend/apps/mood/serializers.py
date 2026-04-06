from rest_framework import serializers
from django.utils import timezone
from .models import MoodEntry


class MoodEntrySerializer(serializers.ModelSerializer):
    mood_score = serializers.ReadOnlyField()
    mood_emoji = serializers.ReadOnlyField()

    class Meta:
        model = MoodEntry
        fields = ['id', 'mood', 'note', 'date', 'mood_score', 'mood_emoji',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'mood_score', 'mood_emoji']

    def validate_date(self, value):
        """Don't allow future dates."""
        if value > timezone.now().date():
            raise serializers.ValidationError("Cannot log mood for a future date.")
        return value

    def validate_note(self, value):
        """Sanitize note field."""
        if value:
            # Strip extra whitespace, limit length
            return value.strip()[:500]
        return value


class MoodStatsSerializer(serializers.Serializer):
    """Serializer for mood statistics/analytics response."""
    period = serializers.CharField()
    entries = MoodEntrySerializer(many=True)
    average_score = serializers.FloatField()
    most_common_mood = serializers.CharField()
    mood_distribution = serializers.DictField()
    total_entries = serializers.IntegerField()
