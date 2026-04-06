"""
Authentication URL Routes
=========================
Maps URLs to view functions.
All these URLs are prefixed with /api/auth/ (set in main urls.py)
"""

from django.urls import path
from .views import RegisterView, LoginView, TokenRefreshView, MeView

urlpatterns = [
    # POST /api/auth/register/ → Create new anonymous user
    path('register/', RegisterView.as_view(), name='register'),

    # POST /api/auth/login/ → Login with UUID
    path('login/', LoginView.as_view(), name='login'),

    # POST /api/auth/token/refresh/ → Get new access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # GET /api/auth/me/ → Get current user info
    path('me/', MeView.as_view(), name='me'),
]
