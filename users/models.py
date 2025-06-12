from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')

    class ReligiousView(models.TextChoices):
        SUNNI = 'SUNNI', _('Sunni')
        SHIA = 'SHIA', _('Shia')
        OTHER = 'OTHER', _('Other')

    class RelationshipGoal(models.TextChoices):
        MARRIAGE = 'MARRIAGE', _('Marriage')
        HALAL_DATING = 'HALAL_DATING', _('Halal Dating')
        FRIENDSHIP = 'FRIENDSHIP', _('Friendship')

    # Basic Info
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    
    # Profile Info
    gender = models.CharField(_('gender'), max_length=1, choices=Gender.choices)
    birth_date = models.DateField(_('birth date'), null=True)
    height = models.PositiveIntegerField(_('height in cm'), null=True)
    ethnicity = models.CharField(_('ethnicity'), max_length=100)
    religious_view = models.CharField(_('religious view'), max_length=10, choices=ReligiousView.choices)
    relationship_goal = models.CharField(_('relationship goal'), max_length=20, choices=RelationshipGoal.choices)
    
    # Location
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, null=True)
    location_visible = models.BooleanField(_('location visible'), default=True)
    
    # Profile Features
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    voice_bio = models.FileField(_('voice bio'), upload_to='voice_bios/', null=True, blank=True)
    is_verified = models.BooleanField(_('is verified'), default=False)
    is_premium = models.BooleanField(_('is premium'), default=False)
    
    # Preferences
    min_age = models.PositiveIntegerField(_('minimum age preference'), default=18)
    max_age = models.PositiveIntegerField(_('maximum age preference'), default=99)
    max_distance = models.PositiveIntegerField(_('maximum distance in km'), default=100)
    
    # Stats
    last_active = models.DateTimeField(_('last active'), auto_now=True)
    profile_views = models.PositiveIntegerField(_('profile views'), default=0)
    roses_received = models.PositiveIntegerField(_('roses received'), default=0)
    
    # Settings
    show_online_status = models.BooleanField(_('show online status'), default=True)
    allow_messages = models.BooleanField(_('allow messages'), default=True)
    allow_profile_views = models.BooleanField(_('allow profile views'), default=True)
    
    # Social
    instagram_handle = models.CharField(_('instagram handle'), max_length=30, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'gender']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

class UserPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(_('photo'), upload_to='user_photos/')
    is_primary = models.BooleanField(_('is primary photo'), default=False)
    order = models.PositiveIntegerField(_('display order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = _('user photo')
        verbose_name_plural = _('user photos')

    def __str__(self):
        return f"{self.user.username}'s photo {self.order}"

class UserPrompt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompts')
    question = models.CharField(_('prompt question'), max_length=200)
    answer = models.TextField(_('prompt answer'), max_length=500)
    order = models.PositiveIntegerField(_('display order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = _('user prompt')
        verbose_name_plural = _('user prompts')

    def __str__(self):
        return f"{self.user.username}'s prompt: {self.question}" 