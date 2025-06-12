from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, MessageReaction, MessageReport

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    match = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'match', 'sender', 'content', 'message_type',
            'media_url', 'is_read', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class MessageCreateSerializer(serializers.ModelSerializer):
    match_id = serializers.PrimaryKeyRelatedField(
        source='match',
        queryset=Message.match.field.related_model.objects.all()
    )

    class Meta:
        model = Message
        fields = ['match_id', 'content', 'message_type', 'media_url']

    def validate(self, attrs):
        match = attrs['match']
        user = self.context['request'].user

        # Check if user is part of the match
        if user not in match.users.all():
            raise serializers.ValidationError("You are not part of this match")

        # Check if match is active
        if not match.is_active:
            raise serializers.ValidationError("This match is no longer active")

        return attrs

class MessageReactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    message = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MessageReaction
        fields = ['id', 'message', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['id', 'created_at']

class MessageReactionCreateSerializer(serializers.ModelSerializer):
    message_id = serializers.PrimaryKeyRelatedField(
        source='message',
        queryset=Message.objects.all()
    )

    class Meta:
        model = MessageReaction
        fields = ['message_id', 'reaction_type']

    def validate(self, attrs):
        message = attrs['message']
        user = self.context['request'].user

        # Check if user is part of the match
        if user not in message.match.users.all():
            raise serializers.ValidationError("You are not part of this match")

        return attrs

class MessageReportSerializer(serializers.ModelSerializer):
    reporter = serializers.PrimaryKeyRelatedField(read_only=True)
    message = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MessageReport
        fields = [
            'id', 'message', 'reporter', 'reason',
            'description', 'created_at', 'is_resolved'
        ]
        read_only_fields = ['id', 'created_at', 'is_resolved']

class MessageReportCreateSerializer(serializers.ModelSerializer):
    message_id = serializers.PrimaryKeyRelatedField(
        source='message',
        queryset=Message.objects.all()
    )

    class Meta:
        model = MessageReport
        fields = ['message_id', 'reason', 'description']

    def validate(self, attrs):
        message = attrs['message']
        user = self.context['request'].user

        # Check if user is part of the match
        if user not in message.match.users.all():
            raise serializers.ValidationError("You are not part of this match")

        # Check if user has already reported this message
        if MessageReport.objects.filter(message=message, reporter=user).exists():
            raise serializers.ValidationError("You have already reported this message")

        return attrs 