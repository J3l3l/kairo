from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, MessageReactionViewSet, MessageReportViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'reactions', MessageReactionViewSet, basename='reaction')
router.register(r'reports', MessageReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
] 