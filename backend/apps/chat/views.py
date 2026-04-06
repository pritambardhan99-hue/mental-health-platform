"""
Chat Views - REST API for Chat Rooms and Messages
==================================================
These are the HTTP REST endpoints (not WebSocket).
WebSocket is handled by consumers.py.

HTTP endpoints are used for:
- Creating rooms
- Loading message history
- Getting room list

Real-time messaging uses WebSocket (consumers.py)
"""

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, CreateRoomSerializer, MessageSerializer


class MessagePagination(PageNumberPagination):
    """Load 50 messages per page for chat history."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatRoomListCreateView(APIView):
    """
    GET  /api/chat/rooms/     → List user's chat rooms
    POST /api/chat/rooms/     → Create new chat room
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all rooms belonging to the current user."""
        rooms = ChatRoom.objects.filter(created_by=request.user)
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new chat room for the current user."""
        serializer = CreateRoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(created_by=request.user)
            return Response(
                ChatRoomSerializer(room).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatRoomDetailView(APIView):
    """
    GET /api/chat/rooms/<room_id>/ → Get room details and messages
    """
    permission_classes = [IsAuthenticated]

    def get_room(self, room_id, user):
        """Get room, ensuring it belongs to current user."""
        try:
            return ChatRoom.objects.get(id=room_id, created_by=user)
        except ChatRoom.DoesNotExist:
            return None

    def get(self, request, room_id):
        room = self.get_room(room_id, request.user)
        if not room:
            return Response(
                {'error': 'Room not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Paginate messages for performance
        messages = room.messages.all()
        paginator = MessagePagination()
        page = paginator.paginate_queryset(messages, request)
        serializer = MessageSerializer(page, many=True)

        return paginator.get_paginated_response({
            'room': ChatRoomSerializer(room).data,
            'messages': serializer.data
        })


class CreateOrGetDefaultRoom(APIView):
    """
    POST /api/chat/rooms/default/
    
    Creates or returns the user's default "My Safe Space" room.
    Used when user first opens the chat — no need to manually create a room.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        room, created = ChatRoom.objects.get_or_create(
            created_by=request.user,
            name='My Safe Space',
            defaults={'name': 'My Safe Space'}
        )
        serializer = ChatRoomSerializer(room)
        return Response({
            **serializer.data,
            'is_new': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
