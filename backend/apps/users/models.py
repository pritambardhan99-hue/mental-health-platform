"""
Anonymous User Model
====================
CONCEPT: Instead of asking for email/password, we generate a random UUID
for each new visitor. This UUID becomes their identity.

WHY UUID?
- Universally Unique: mathematically near-impossible to guess
- Anonymous: no personal information attached
- Persistent: user can save their UUID and return later

DATABASE TABLE: users_anonymoususer
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class AnonymousUserManager(BaseUserManager):
    """
    Custom manager for AnonymousUser.
    
    A "manager" in Django is the interface for database queries.
    BaseUserManager provides helper methods for creating users.
    """

    def create_user(self):
        """
        Create a new anonymous user with just a UUID.
        No email, no username, no password required!
        """
        user = self.model()  # Create empty user object
        user.set_unusable_password()  # Mark that this user has no password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        """
        Create a Django admin superuser (for admin panel access).
        This IS password-protected for security.
        """
        user = self.model(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class AnonymousUser(AbstractBaseUser, PermissionsMixin):
    """
    Our custom User model.
    
    AbstractBaseUser: Gives us authentication methods (is_authenticated, etc.)
    PermissionsMixin: Gives us is_staff, is_superuser, groups, permissions
    
    FIELDS:
    - id: UUID primary key (not a simple 1, 2, 3 integer — much harder to guess)
    - created_at: When this anonymous session was created
    - last_active: Updated each time user makes a request
    - username: Only for admin users (null for anonymous)
    """

    # UUID primary key - e.g., "550e8400-e29b-41d4-a716-446655440000"
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,  # Automatically generates a new UUID
        editable=False,
        help_text="Unique anonymous identifier for this user"
    )

    # For admin superusers only (null/blank for anonymous users)
    username = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True,
        help_text="Only used for admin accounts"
    )

    # Timestamp fields - Django automatically fills these
    created_at = models.DateTimeField(
        auto_now_add=True,  # Set when object is first created
        help_text="When this anonymous session started"
    )
    last_active = models.DateTimeField(
        auto_now=True,  # Updated every time the object is saved
        help_text="Last time user was seen"
    )

    # Required for Django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Tell Django which field is the "username" for authentication
    # We use UUID id, but for admin users we use username
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    # Connect our custom manager
    objects = AnonymousUserManager()

    class Meta:
        db_table = 'anonymous_users'
        verbose_name = 'Anonymous User'
        verbose_name_plural = 'Anonymous Users'

    def __str__(self):
        return f"Anon-{str(self.id)[:8]}"  # Show first 8 chars of UUID

    def update_last_active(self):
        """Helper method to update last_active timestamp."""
        from django.utils import timezone
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])
