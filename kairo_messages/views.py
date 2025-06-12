from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Message, MessageReaction, MessageReport
from .serializers import (
    MessageSerializer, MessageCreateSerializer,
    MessageReactionSerializer, MessageReactionCreateSerializer,
    MessageReportSerializer, MessageReportCreateSerializer
)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            match__users=self.request.user,
            is_deleted=False
        ).select_related('sender', 'match')

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        # Update match's last_message_at
        message.match.last_message_at = timezone.now()
        message.match.save()

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if not message.is_read:
            message.is_read = True
            message.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        message = self.get_object()
        if message.sender == request.user:
            message.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "You can only delete your own messages"},
            status=status.HTTP_403_FORBIDDEN
        )

class MessageReactionViewSet(viewsets.ModelViewSet):
    serializer_class = MessageReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MessageReaction.objects.filter(
            message__match__users=self.request.user
        ).select_related('user', 'message')

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageReactionCreateSerializer
        return MessageReactionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class MessageReportViewSet(viewsets.ModelViewSet):
    serializer_class = MessageReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MessageReport.objects.filter(
            message__match__users=self.request.user
        ).select_related('reporter', 'message')

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageReportCreateSerializer
        return MessageReportSerializer

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user) 