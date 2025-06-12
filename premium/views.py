from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import stripe
from django.conf import settings
from .models import Subscription, RoseBalance, Boost, InviteCode
from .serializers import (
    SubscriptionSerializer, RoseBalanceSerializer,
    BoostSerializer, InviteCodeSerializer,
    InviteCodeCreateSerializer, InviteCodeUseSerializer
)

stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_subscription(self, request):
        try:
            # Create Stripe customer
            customer = stripe.Customer.create(
                email=request.user.email,
                source=request.data['token']
            )

            # Create Stripe subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': request.data['price_id']}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )

            # Create local subscription
            local_subscription = Subscription.objects.create(
                user=request.user,
                stripe_customer_id=customer.id,
                stripe_subscription_id=subscription.id,
                plan_type=request.data['plan_type'],
                current_period_start=timezone.now(),
                current_period_end=timezone.now() + timedelta(days=30)
            )

            # Update user's premium status
            request.user.is_premium = True
            request.user.save()

            return Response(SubscriptionSerializer(local_subscription).data)
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel_subscription(self, request, pk=None):
        subscription = self.get_object()
        try:
            # Cancel Stripe subscription
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            stripe_sub.delete()

            # Update local subscription
            subscription.is_active = False
            subscription.cancel_at_period_end = True
            subscription.save()

            # Update user's premium status
            request.user.is_premium = False
            request.user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class RoseBalanceViewSet(viewsets.ModelViewSet):
    serializer_class = RoseBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RoseBalance.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def reset_daily(self, request):
        balance, created = RoseBalance.objects.get_or_create(
            user=request.user,
            defaults={'balance': 3}
        )
        
        if not created and (timezone.now() - balance.last_reset).days >= 1:
            balance.balance = 3
            balance.last_reset = timezone.now()
            balance.save()
        
        return Response(RoseBalanceSerializer(balance).data)

class BoostViewSet(viewsets.ModelViewSet):
    serializer_class = BoostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Boost.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def activate(self, request):
        # Check if user has an active boost
        if Boost.objects.filter(user=request.user, is_active=True).exists():
            return Response(
                {'error': 'You already have an active boost'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create new boost
        boost = Boost.objects.create(
            user=request.user,
            end_time=timezone.now() + timedelta(hours=24)
        )

        return Response(BoostSerializer(boost).data)

class InviteCodeViewSet(viewsets.ModelViewSet):
    serializer_class = InviteCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InviteCode.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return InviteCodeCreateSerializer
        return InviteCodeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def use_code(self, request):
        serializer = InviteCodeUseSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            invite_code = InviteCode.objects.get(code=code)
            
            # Update invite code
            invite_code.is_used = True
            invite_code.used_by = request.user
            invite_code.used_at = timezone.now()
            invite_code.save()

            # Add rose to user's balance
            balance, created = RoseBalance.objects.get_or_create(
                user=request.user,
                defaults={'balance': 1}
            )
            if not created:
                balance.balance += 1
                balance.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 