from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Message(models.Model):
    class MessageType(models.TextChoices):
        TEXT = 'TEXT', _('Text')
        IMAGE = 'IMAGE', _('Image')
        VOICE = 'VOICE', _('Voice')

    match = models.ForeignKey(
        'matches.Match',
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField(_('content'))
    message_type = models.CharField(
        max_length=10,
        choices=MessageType.choices,
        default=MessageType.TEXT
    )
    media_url = models.URLField(_('media URL'), blank=True)
    is_read = models.BooleanField(_('is read'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(_('is deleted'), default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in match {self.match.id}"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

class MessageReaction(models.Model):
    class ReactionType(models.TextChoices):
        LIKE = 'LIKE', _('Like')
        LOVE = 'LOVE', _('Love')
        LAUGH = 'LAUGH', _('Laugh')
        WOW = 'WOW', _('Wow')
        SAD = 'SAD', _('Sad')
        ANGRY = 'ANGRY', _('Angry')

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_reactions'
    )
    reaction_type = models.CharField(
        max_length=10,
        choices=ReactionType.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction_type} to message {self.message.id}"

class MessageReport(models.Model):
    class ReportReason(models.TextChoices):
        INAPPROPRIATE = 'INAPPROPRIATE', _('Inappropriate Content')
        HARASSMENT = 'HARASSMENT', _('Harassment')
        SPAM = 'SPAM', _('Spam')
        OTHER = 'OTHER', _('Other')

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_reports'
    )
    reason = models.CharField(
        max_length=20,
        choices=ReportReason.choices
    )
    description = models.TextField(_('description'), max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(_('is resolved'), default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on message {self.message.id} by {self.reporter.username}" 