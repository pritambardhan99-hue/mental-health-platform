"""
Users Views - Authentication API
=================================
These views handle anonymous user registration and token management.

FLOW:
1. User visits the app for the first time
2. Frontend calls POST /api/auth/register/
3. Backend creates anonymous user, generates UUID + JWT
4. Frontend stores UUID and JWT in localStorage
5. Every subsequent API call includes JWT in Authorization header

ANONYMOUS LOGIN FLOW:
1. User has their UUID saved (from previous session)
2. Frontend calls POST /api/auth/login/ with UUID
3. Backend finds user by UUID, issues new JWT tokens
4. User is back in their session!
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import AnonymousUser
from .serializers import AnonymousUserSerializer, RegisterResponseSerializer


class RegisterView(APIView):
    """
    POST /api/auth/register/
    
    Creates a new anonymous user. No body required!
    Returns: UUID + JWT tokens
    
    Example Response:
    {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "access_token": "eyJ0eXAiOiJKV1Q...",
        "refresh_token": "eyJ0eXAiOiJKV1Q...",
        "message": "Anonymous session created. Save your user_id to return!"
    }
    """
    permission_classes = [AllowAny]  # No authentication needed to register

    def post(self, request):
        # Create new anonymous user (just generates a UUID)
        user = AnonymousUser.objects.create_user()

        # Generate JWT tokens for this user
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'user_id': str(user.id),
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'message': 'Anonymous session created. Save your user_id to return to your account!'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/auth/login/
    
    Allows a returning anonymous user to get new JWT tokens using their UUID.
    
    Request Body:
    {
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    
    Response:
    {
        "access_token": "eyJ0eXAiOiJKV1Q...",
        "refresh_token": "eyJ0eXAiOiJKV1Q..."
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required. This is your anonymous identity UUID.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Look up user by their UUID
            user = AnonymousUser.objects.get(id=user_id)
        except AnonymousUser.DoesNotExist:
            return Response(
                {'error': 'No account found with this user_id. '
                          'Did you save your UUID? Try registering for a new session.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {'error': 'Invalid UUID format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update last_active timestamp
        user.update_last_active()

        # Generate fresh JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': str(user.id),
            'message': 'Welcome back!'
        }, status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    """
    POST /api/auth/token/refresh/
    
    Get a new access token using a refresh token.
    Access tokens expire after 7 days; use this to get a new one.
    
    Request Body:
    {
        "refresh": "eyJ0eXAiOiJKV1Q..."
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access_token': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response(
                {'error': f'Invalid or expired refresh token: {str(e)}'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class MeView(APIView):
    """
    GET /api/auth/me/
    
    Returns the current user's information.
    Requires: Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = AnonymousUserSerializer(user)
        return Response(serializer.data)
