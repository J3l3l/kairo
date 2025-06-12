from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Like(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes_sent'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes_received'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.username} liked {self.to_user.username}"

class Rose(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roses_sent'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roses_received_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(_('message'), max_length=500, blank=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.username} sent a rose to {self.to_user.username}"

class Match(models.Model):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='matches'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-last_message_at', '-created_at']

    def __str__(self):
        return f"Match between {', '.join(user.username for user in self.users.all())}"

class Unmatch(models.Model):
    class Reason(models.TextChoices):
        GHOSTED = 'GHOSTED', _('Ghosted')
        INAPPROPRIATE = 'INAPPROPRIATE', _('Inappropriate Behavior')
        NO_CONNECTION = 'NO_CONNECTION', _('No Connection')
        OTHER = 'OTHER', _('Other')

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='unmatches'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='unmatches'
    )
    reason = models.CharField(
        max_length=20,
        choices=Reason.choices,
        default=Reason.OTHER
    )
    feedback = models.TextField(_('feedback'), max_length=500, blank=True)
    rating = models.PositiveSmallIntegerField(_('rating'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} unmatched: {self.reason}"

class ProfileView(models.Model):
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='views_sent'
    )
    viewed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='views_received'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        unique_together = ('viewer', 'viewed_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.viewer.username} viewed {self.viewed_user.username}'s profile" 