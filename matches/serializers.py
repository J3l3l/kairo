from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Like, Rose, Match, Unmatch, ProfileView

User = get_user_model()

class LikeSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Like
        fields = ['id', 'from_user', 'to_user', 'created_at']
        read_only_fields = ['id', 'created_at']

class RoseSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Rose
        fields = ['id', 'from_user', 'to_user', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

class MatchSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ['id', 'users', 'other_user', 'created_at', 'last_message_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'last_message_at']

    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and request.user in obj.users.all():
            other_user = obj.users.exclude(id=request.user.id).first()
            if other_user:
                return {
                    'id': other_user.id,
                    'username': other_user.username,
                    'first_name': other_user.first_name,
                    'last_name': other_user.last_name,
                    'photo': other_user.photos.filter(is_primary=True).first().image.url if other_user.photos.filter(is_primary=True).exists() else None
                }
        return None

class UnmatchSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    match = serializers.PrimaryKeyRelatedField(queryset=Match.objects.all())

    class Meta:
        model = Unmatch
        fields = ['id', 'match', 'user', 'reason', 'feedback', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']

class ProfileViewSerializer(serializers.ModelSerializer):
    viewer = serializers.PrimaryKeyRelatedField(read_only=True)
    viewed_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ProfileView
        fields = ['id', 'viewer', 'viewed_user', 'created_at', 'is_anonymous']
        read_only_fields = ['id', 'created_at']

class MatchCreateSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate(self, attrs):
        user = attrs['user_id']
        request_user = self.context['request'].user

        # Check if users have liked each other
        if not (Like.objects.filter(from_user=request_user, to_user=user).exists() and
                Like.objects.filter(from_user=user, to_user=request_user).exists()):
            raise serializers.ValidationError("Both users must like each other to create a match")

        # Check if match already exists
        if Match.objects.filter(users=request_user).filter(users=user).exists():
            raise serializers.ValidationError("Match already exists")

        return attrs 