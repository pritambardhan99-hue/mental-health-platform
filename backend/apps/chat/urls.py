from django.urls import path
from .views import ChatRoomListCreateView, ChatRoomDetailView, CreateOrGetDefaultRoom

urlpatterns = [
    path('rooms/', ChatRoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/default/', CreateOrGetDefaultRoom.as_view(), name='default-room'),
    path('rooms/<uuid:room_id>/', ChatRoomDetailView.as_view(), name='room-detail'),
]
