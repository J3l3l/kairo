from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import UserPhoto, UserPrompt
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileUpdateSerializer,
    UserPreferencesSerializer, UserLocationSerializer, UserPhotoSerializer,
    UserPromptSerializer
)
from django.utils import timezone

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(
            Q(gender__in=user.preferences.allowed_genders) &
            Q(birth_date__year__gte=user.min_age) &
            Q(birth_date__year__lte=user.max_age)
        ).exclude(id=user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'])
    def update_preferences(self, request):
        serializer = UserPreferencesSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'])
    def update_location(self, request):
        serializer = UserLocationSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def upload_photo(self, request):
        serializer = UserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_photo(self, request, pk=None):
        try:
            photo = UserPhoto.objects.get(id=pk, user=request.user)
            photo.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserPhoto.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def add_prompt(self, request):
        serializer = UserPromptSerializer(data=request.data)
        if serializer.is_valid():
            prompt = serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_prompt(self, request, pk=None):
        try:
            prompt = UserPrompt.objects.get(id=pk, user=request.user)
            prompt.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserPrompt.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def who_viewed_me(self, request):
        if not request.user.is_premium:
            # For free users, show only 2 random viewers
            viewers = request.user.profile_views.all()[:2]
        else:
            # For premium users, show all viewers
            viewers = request.user.profile_views.all()
        serializer = self.get_serializer(viewers, many=True)
        return Response(serializer.data)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data['email'])
            user.last_active = timezone.now()
            user.save()
        return response 