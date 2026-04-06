"""
Mood Tracking Models
====================
Allows users to log their emotional state each day.

DATABASE TABLE: mood_entries

MOOD CHOICES:
  We use simple string keys so frontend can map them to emojis easily:
  'happy'   → 😊
  'calm'    → 😌
  'anxious' → 😰
  'sad'     → 😢
  'angry'   → 😠
  'hopeful' → 🌟

RELATIONSHIPS:
  MoodEntry → AnonymousUser (ForeignKey)
  One user can have many mood entries (one per day ideally)

CONSTRAINT:
  unique_together = ['user', 'date'] ensures only ONE entry per user per day.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class MoodEntry(models.Model):
    """
    Records a user's mood for a specific date.
    
    DESIGN DECISION: We allow 1 entry per day per user.
    If user submits again on same day, we UPDATE the existing entry.
    This prevents data flooding and gives clean daily data for charts.
    """

    MOOD_CHOICES = [
        ('happy',   'Happy 😊'),
        ('calm',    'Calm 😌'),
        ('anxious', 'Anxious 😰'),
        ('sad',     'Sad 😢'),
        ('angry',   'Angry 😠'),
        ('hopeful', 'Hopeful 🌟'),
        ('numb',    'Numb 😶'),
        ('overwhelmed', 'Overwhelmed 😩'),
    ]

    # Numeric score for charting (used to plot mood trend lines)
    MOOD_SCORES = {
        'happy': 5,
        'hopeful': 4,
        'calm': 4,
        'numb': 3,
        'anxious': 2,
        'angry': 2,
        'sad': 1,
        'overwhelmed': 1,
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mood_entries',
        help_text="The anonymous user this mood belongs to"
    )

    mood = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        help_text="User's mood selection"
    )

    # Optional text note about how they're feeling
    note = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text="Optional note about the mood (max 500 chars)"
    )

    # The date this mood was recorded for (not timestamp — just the date)
    date = models.DateField(
        default=timezone.now,
        help_text="The date this mood was recorded"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mood_entries'
        # One mood entry per user per day
        unique_together = ['user', 'date']
        ordering = ['-date']  # Most recent first

    def __str__(self):
        return f"{self.user} felt {self.mood} on {self.date}"

    @property
    def mood_score(self):
        """Returns a numeric score (1-5) for charting purposes."""
        return self.MOOD_SCORES.get(self.mood, 3)

    @property
    def mood_emoji(self):
        """Returns the emoji for this mood."""
        emojis = {
            'happy': '😊', 'calm': '😌', 'anxious': '😰',
            'sad': '😢', 'angry': '😠', 'hopeful': '🌟',
            'numb': '😶', 'overwhelmed': '😩',
        }
        return emojis.get(self.mood, '😶')
