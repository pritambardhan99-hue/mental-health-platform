import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from groq import Groq

from apps.chat.models import ChatRoom, Message
from apps.emergency.utils import detect_emergency_keywords, get_severity, HELPLINE_RESOURCES
from apps.emergency.models import EmergencyLog

logger = logging.getLogger(__name__)

MENTAL_HEALTH_SYSTEM_PROMPT = """You are Serene, a warm, empathetic, and non-judgmental mental health support companion.

Your core principles:
1. EMPATHY FIRST: Always acknowledge feelings before offering advice.
2. NEVER DIAGNOSE: You are NOT a therapist or doctor.
3. NEVER PRESCRIBE: Never suggest medications or dosages.
4. VALIDATE: Make users feel heard and not alone.
5. COPING STRATEGIES: Offer evidence-based techniques when appropriate.
6. PROFESSIONAL HELP: Gently encourage professional support when needed.
7. CRISIS DETECTION: If someone mentions suicide or self-harm, respond with compassion AND provide crisis resources.
8. LANGUAGE: Use simple, warm language. Speak like a caring friend.
9. BOUNDARIES: You provide SUPPORT, not therapy.
10. CULTURAL SENSITIVITY: Be aware of diverse backgrounds.

Keep responses concise (2-4 paragraphs max).
Remember: Your goal is to make each person feel less alone.
"""


class ChatbotMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message', '').strip()
        room_id = request.data.get('room_id')
        conversation_history = request.data.get('conversation_history', [])

        if not user_message:
            return Response(
                {'error': 'Message cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Emergency detection
        is_emergency, keywords_found = detect_emergency_keywords(user_message)

        if is_emergency:
            severity = get_severity(keywords_found)
            EmergencyLog.objects.create(
                user=request.user,
                detected_text=user_message,
                keywords_found=keywords_found,
                severity=severity,
                source='chatbot',
                alert_triggered=True
            )

        # Get or create room
        room = None
        if room_id:
            try:
                room = ChatRoom.objects.get(id=room_id, created_by=request.user)
            except ChatRoom.DoesNotExist:
                pass

        if not room:
            room, _ = ChatRoom.objects.get_or_create(
                created_by=request.user,
                name='My Safe Space'
            )

        # Save user message
        user_msg_obj = Message.objects.create(
            room=room,
            sender=request.user,
            sender_type='user',
            message_text=user_message,
            is_flagged=is_emergency
        )

        # Call Groq AI
        try:
            ai_response_text = self._call_groq(
                user_message,
                conversation_history,
                is_emergency
            )
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            ai_response_text = (
                "I'm having trouble connecting right now. "
                "But I'm here with you. "
                "If this is urgent, please reach out to a helpline."
            )

        # Save AI response
        ai_msg_obj = Message.objects.create(
            room=room,
            sender=None,
            sender_type='ai',
            message_text=ai_response_text,
            is_flagged=False
        )

        response_data = {
            'response': ai_response_text,
            'is_emergency': is_emergency,
            'room_id': str(room.id),
            'user_message_id': str(user_msg_obj.id),
            'ai_message_id': str(ai_msg_obj.id),
        }

        if is_emergency:
            response_data['emergency_resources'] = HELPLINE_RESOURCES
            response_data['severity'] = get_severity(keywords_found)

        return Response(response_data, status=status.HTTP_200_OK)

    def _call_groq(self, user_message, conversation_history, is_emergency):
        client = Groq(api_key=settings.OPENAI_API_KEY)

        # Start with system prompt
        messages = [{"role": "system", "content": MENTAL_HEALTH_SYSTEM_PROMPT}]

        # Add conversation history
        for msg in conversation_history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content and role in ("user", "assistant"):
                messages.append({"role": role, "content": content})

        # Add emergency note if needed
        if is_emergency:
            user_message += "\n[Please respond with extra compassion and mention crisis helpline resources.]"

        # Add current message
        messages.append({"role": "user", "content": user_message})

        # Call Groq
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        return response.choices[0].message.content


class ChatbotHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        room_id = request.query_params.get('room_id')

        if room_id:
            try:
                room = ChatRoom.objects.get(id=room_id, created_by=request.user)
            except ChatRoom.DoesNotExist:
                return Response(
                    {'error': 'Room not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            room, _ = ChatRoom.objects.get_or_create(
                created_by=request.user,
                name='My Safe Space'
            )

        messages = Message.objects.filter(room=room).order_by('timestamp')[:100]

        data = [{
            'id': str(m.id),
            'role': 'assistant' if m.sender_type == 'ai' else 'user',
            'content': m.message_text,
            'sender_type': m.sender_type,
            'timestamp': m.timestamp.isoformat(),
            'is_flagged': m.is_flagged,
        } for m in messages]

        return Response({
            'room_id': str(room.id),
            'messages': data,
            'total': len(data)
        })