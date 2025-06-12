from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Like, Rose, Match, Unmatch, ProfileView
from .serializers import (
    LikeSerializer, RoseSerializer, MatchSerializer,
    UnmatchSerializer, ProfileViewSerializer, MatchCreateSerializer
)

class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(from_user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

        # Check if it's a mutual like
        if Like.objects.filter(from_user=serializer.validated_data['to_user'],
                             to_user=self.request.user).exists():
            # Create a match
            match = Match.objects.create()
            match.users.add(self.request.user, serializer.validated_data['to_user'])
            match.save()

class RoseViewSet(viewsets.ModelViewSet):
    serializer_class = RoseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rose.objects.filter(from_user=self.request.user)

    def perform_create(self, serializer):
        # Check if user has roses available
        if not self.request.user.is_premium:
            roses_sent_today = Rose.objects.filter(
                from_user=self.request.user,
                created_at__date=timezone.now().date()
            ).count()
            if roses_sent_today >= 3:
                raise permissions.PermissionDenied("Daily rose limit reached")
        
        serializer.save(from_user=self.request.user)

class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Match.objects.filter(users=self.request.user, is_active=True)

    @action(detail=True, methods=['post'])
    def unmatch(self, request, pk=None):
        match = self.get_object()
        serializer = UnmatchSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(
                match=match,
                user=request.user
            )
            match.is_active = False
            match.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileViewViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileViewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProfileView.objects.filter(viewer=self.request.user)

    def perform_create(self, serializer):
        # Check if user is premium for anonymous viewing
        if serializer.validated_data.get('is_anonymous', False) and not self.request.user.is_premium:
            raise permissions.PermissionDenied("Anonymous viewing is a premium feature")
        
        serializer.save(viewer=self.request.user)

    @action(detail=False, methods=['get'])
    def who_viewed_me(self, request):
        if not request.user.is_premium:
            # For free users, show only 2 random viewers
            viewers = ProfileView.objects.filter(
                viewed_user=request.user
            ).order_by('?')[:2]
        else:
            # For premium users, show all viewers
            viewers = ProfileView.objects.filter(
                viewed_user=request.user
            ).order_by('-created_at')
        
        serializer = self.get_serializer(viewers, many=True)
        return Response(serializer.data) 