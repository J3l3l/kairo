from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Subscription, RoseBalance, Boost, InviteCode

User = get_user_model()

class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'stripe_customer_id', 'stripe_subscription_id',
            'plan_type', 'is_active', 'current_period_start',
            'current_period_end', 'cancel_at_period_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_customer_id', 'stripe_subscription_id',
            'current_period_start', 'current_period_end',
            'created_at', 'updated_at'
        ]

class RoseBalanceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RoseBalance
        fields = [
            'id', 'user', 'balance', 'last_reset',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class BoostSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Boost
        fields = [
            'id', 'user', 'start_time', 'end_time',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class InviteCodeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    used_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = InviteCode
        fields = [
            'id', 'user', 'code', 'is_used',
            'used_by', 'created_at', 'used_at'
        ]
        read_only_fields = ['id', 'created_at', 'used_at']

class InviteCodeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteCode
        fields = ['code']

    def validate_code(self, value):
        if InviteCode.objects.filter(code=value, is_used=False).exists():
            raise serializers.ValidationError("This invite code is already in use")
        return value

class InviteCodeUseSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)

    def validate_code(self, value):
        try:
            invite_code = InviteCode.objects.get(code=value, is_used=False)
        except InviteCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used invite code")
        return value 