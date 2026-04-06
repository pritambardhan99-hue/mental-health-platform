"""
Chat Consumers (WebSocket Handlers)
=====================================
A "consumer" in Django Channels is like a "view" but for WebSockets.

HOW WEBSOCKETS WORK:
  Normal HTTP:  Client → Request → Server → Response → Connection Closed
  WebSocket:    Client → Connect → Server → PERSISTENT connection → Messages flow both ways

FLOW:
  1. React frontend opens WebSocket: ws://localhost:8000/ws/chat/<room_id>/
  2. connect() is called → user joins a "channel group" (like a chat room)
  3. User sends message → receive() is called → message saved to DB
  4. Message broadcast to everyone in the group via Redis
  5. disconnect() → user leaves the group

REDIS ROLE:
  Redis acts as a "message broker" between multiple server instances.
  Without Redis, WebSocket messages would only go to users on the SAME server.
  With Redis, messages are shared across ALL server instances → scalable!
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for the chat feature.
    
    'Async' means it can handle many simultaneous connections efficiently
    without blocking — crucial for a real-time chat system.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is first established.
        
        Steps:
        1. Extract room_id from URL
        2. Authenticate user via JWT token in query string
        3. Add user to the room's channel group
        4. Accept the WebSocket connection
        """
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Authenticate the WebSocket connection using JWT
        # The token is passed as a query parameter: ws://...?token=<jwt>
        try:
            query_string = self.scope.get('query_string', b'').decode('utf-8')
            params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            token_str = params.get('token', '')

            if not token_str:
                logger.warning("WebSocket connection rejected: No token provided")
                await self.close(code=4001)
                return

            # Validate the JWT token
            token = AccessToken(token_str)
            user_id = token['user_id']

            # Load user from database
            self.user = await self.get_user(user_id)
            if not self.user:
                await self.close(code=4002)
                return

        except (TokenError, KeyError, ValueError) as e:
            logger.error(f"WebSocket auth failed: {e}")
            await self.close(code=4003)
            return

        # Verify user has access to this room
        has_access = await self.check_room_access(self.room_id, self.user)
        if not has_access:
            await self.close(code=4004)
            return

        # Join the channel group for this room
        # All users in this group receive broadcasted messages
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Send a welcome message
        await self.send(text_data=json.dumps({
            'type': 'system',
            'message': 'Connected to your safe space. You are not alone. 💙',
            'timestamp': timezone.now().isoformat()
        }))

        logger.info(f"User {self.user.id} connected to room {self.room_id}")

    async def disconnect(self, close_code):
        """
        Called when WebSocket connection is closed.
        Remove user from the channel group.
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"User disconnected from room {self.room_id} (code: {close_code})")

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket client.
        
        Steps:
        1. Parse the incoming JSON message
        2. Check for emergency keywords
        3. Save message to database
        4. Broadcast to everyone in the room group
        """
        try:
            data = json.loads(text_data)
            message_text = data.get('message', '').strip()

            if not message_text:
                return

            # Check for emergency keywords BEFORE saving
            is_emergency, keywords_found = await self.check_emergency(message_text)

            # Save message to MySQL database
            message = await self.save_message(
                room_id=self.room_id,
                sender=self.user,
                text=message_text,
                is_flagged=is_emergency
            )

            # Broadcast message to everyone in the room
            # group_send routes the message to all connected WebSockets in the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',  # This calls the chat_message() method
                    'message': message_text,
                    'sender_id': str(self.user.id),
                    'sender_type': 'user',
                    'message_id': str(message.id),
                    'timestamp': message.timestamp.isoformat(),
                    'is_emergency': is_emergency,
                }
            )

            # If emergency detected, send alert
            if is_emergency:
                await self.send_emergency_alert(keywords_found)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {e}")

    async def chat_message(self, event):
        """
        Called by group_send to deliver a message to this specific WebSocket.
        
        This is the "handler" for 'type': 'chat_message' events.
        The naming convention is important: 'chat_message' type → chat_message() method.
        """
        # Send the message data to the WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_type': event['sender_type'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
            'is_emergency': event.get('is_emergency', False),
        }))

    async def send_emergency_alert(self, keywords_found):
        """Send emergency help resources when dangerous keywords detected."""
        emergency_message = {
            'type': 'emergency',
            'message': '🚨 We noticed some concerning words. You matter and help is available.',
            'resources': [
                {
                    'name': 'iCall (India)',
                    'number': '9152987821',
                    'available': 'Mon-Sat, 8am-10pm'
                },
                {
                    'name': 'Vandrevala Foundation',
                    'number': '1860-2662-345',
                    'available': '24/7'
                },
                {
                    'name': 'NIMHANS (India)',
                    'number': '080-46110007',
                    'available': '24/7'
                },
                {
                    'name': 'Crisis Text Line',
                    'number': 'Text HOME to 741741',
                    'available': '24/7'
                },
            ],
            'message_detail': f'Keywords detected: {", ".join(keywords_found)}',
            'timestamp': timezone.now().isoformat()
        }
        await self.send(text_data=json.dumps(emergency_message))

    # ─────────────────────────────────────────────────────────────
    # DATABASE HELPERS
    # These methods bridge async WebSocket code with sync Django ORM
    # database_sync_to_async wraps sync Django DB calls for async use
    # ─────────────────────────────────────────────────────────────

    @database_sync_to_async
    def get_user(self, user_id):
        """Fetch user from database by UUID."""
        from apps.users.models import AnonymousUser
        try:
            return AnonymousUser.objects.get(id=user_id)
        except AnonymousUser.DoesNotExist:
            return None

    @database_sync_to_async
    def check_room_access(self, room_id, user):
        """Verify the user has access to the requested room."""
        from apps.chat.models import ChatRoom
        try:
            room = ChatRoom.objects.get(id=room_id)
            # Only allow the room creator to access it
            return room.created_by == user
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, room_id, sender, text, is_flagged=False):
        """Save a message to the MySQL database."""
        from apps.chat.models import ChatRoom, Message
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(
            room=room,
            sender=sender,
            sender_type='user',
            message_text=text,
            is_flagged=is_flagged
        )

    @database_sync_to_async
    def check_emergency(self, text):
        """
        Check if message contains emergency keywords.
        Returns: (is_emergency: bool, keywords_found: list)
        """
        from apps.emergency.utils import detect_emergency_keywords
        return detect_emergency_keywords(text)
