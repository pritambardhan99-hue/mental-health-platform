"""
Emergency Log Model
===================
Records every instance where emergency keywords were detected.

PURPOSE:
  - Safety audit trail
  - Analyze patterns (anonymously) to improve keyword detection
  - Could be used by platform admins to improve safety systems

DATABASE TABLE: emergency_logs

PRIVACY NOTE:
  We store detected_text for safety auditing only.
  This data should be handled with extreme care.
"""

from django.db import models
from django.conf import settings


class EmergencyLog(models.Model):
    """
    Logs detected emergency keyword events.
    """

    SEVERITY_CHOICES = [
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    SOURCE_CHOICES = [
        ('chat', 'Chat Message'),
        ('chatbot', 'AI Chatbot'),
        ('mood_note', 'Mood Note'),
    ]

    # The user whose message triggered the alert
    # SET_NULL: keep log even if user account is deleted (important for safety records)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='emergency_logs',
        help_text="User whose message triggered the emergency detection"
    )

    # The text that triggered the detection (for review/audit)
    detected_text = models.TextField(
        help_text="The message text that triggered emergency detection"
    )

    # Which keywords were found
    keywords_found = models.JSONField(
        default=list,
        help_text="List of emergency keywords detected in the message"
    )

    # Severity of the detection
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='moderate'
    )

    # Where the text came from
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='chat'
    )

    # Whether the emergency alert was shown to the user
    alert_triggered = models.BooleanField(
        default=True,
        help_text="Whether the emergency resources were shown to the user"
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'emergency_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Emergency [{self.severity}] by {self.user} at {self.timestamp}"
