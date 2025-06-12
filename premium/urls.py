from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionViewSet, RoseBalanceViewSet,
    BoostViewSet, InviteCodeViewSet
)

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'rose-balance', RoseBalanceViewSet, basename='rose-balance')
router.register(r'boosts', BoostViewSet, basename='boost')
router.register(r'invite-codes', InviteCodeViewSet, basename='invite-code')

urlpatterns = [
    path('', include(router.urls)),
] 