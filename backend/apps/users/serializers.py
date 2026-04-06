"""
Users Serializers
=================
Serializers convert between:
  Python objects (Django models) ↔ JSON (what the API sends/receives)

Think of serializers as "translators" between your database and your API.
"""

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AnonymousUser


class AnonymousUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the AnonymousUser model.
    Defines which fields are exposed in API responses.
    """

    class Meta:
        model = AnonymousUser
        # Only expose safe, non-sensitive fields
        fields = ['id', 'created_at', 'last_active']
        read_only_fields = ['id', 'created_at', 'last_active']


class RegisterResponseSerializer(serializers.Serializer):
    """
    Serializer for the registration response.
    
    When a new anonymous user registers, we return:
    1. Their UUID (so they can save it)
    2. An access token (to make authenticated API calls)
    3. A refresh token (to get new access tokens when they expire)
    
    IMPORTANT: Tell users to SAVE their UUID if they want to return later!
    """
    user_id = serializers.UUIDField(help_text="Save this UUID to return to your account")
    access_token = serializers.CharField(help_text="JWT token for API authentication")
    refresh_token = serializers.CharField(help_text="Use this to refresh your access token")
    message = serializers.CharField()

    @staticmethod
    def get_tokens_for_user(user):
        """
        Generate JWT tokens for an anonymous user.
        
        JWT Structure (base64 encoded):
        HEADER.PAYLOAD.SIGNATURE
        
        Our PAYLOAD contains: {'user_id': '<uuid>', 'exp': <timestamp>}
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
