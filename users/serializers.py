from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserPhoto, UserPrompt

User = get_user_model()

class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = ['id', 'image', 'is_primary', 'order']
        read_only_fields = ['id']

class UserPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPrompt
        fields = ['id', 'question', 'answer', 'order']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    photos = UserPhotoSerializer(many=True, read_only=True)
    prompts = UserPromptSerializer(many=True, read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'gender', 'birth_date', 'height', 'ethnicity',
            'religious_view', 'relationship_goal', 'bio',
            'voice_bio', 'is_verified', 'is_premium',
            'min_age', 'max_age', 'max_distance',
            'show_online_status', 'allow_messages',
            'allow_profile_views', 'instagram_handle',
            'photos', 'prompts', 'age'
        ]
        read_only_fields = ['id', 'is_verified', 'is_premium']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password2',
            'first_name', 'last_name', 'gender', 'birth_date',
            'ethnicity', 'religious_view', 'relationship_goal'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'gender': {'required': True},
            'birth_date': {'required': True},
            'ethnicity': {'required': True},
            'religious_view': {'required': True},
            'relationship_goal': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'bio', 'height',
            'ethnicity', 'religious_view', 'relationship_goal',
            'min_age', 'max_age', 'max_distance',
            'show_online_status', 'allow_messages',
            'allow_profile_views', 'instagram_handle'
        ]

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['min_age', 'max_age', 'max_distance']

class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['latitude', 'longitude', 'location_visible'] 