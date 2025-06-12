from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LikeViewSet, RoseViewSet, MatchViewSet, ProfileViewViewSet

router = DefaultRouter()
router.register(r'likes', LikeViewSet, basename='like')
router.register(r'roses', RoseViewSet, basename='rose')
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'profile-views', ProfileViewViewSet, basename='profile-view')

urlpatterns = [
    path('', include(router.urls)),
] 