from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Subscription(models.Model):
    class PlanType(models.TextChoices):
        MONTHLY = 'MONTHLY', _('Monthly')
        YEARLY = 'YEARLY', _('Yearly')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    stripe_customer_id = models.CharField(_('Stripe Customer ID'), max_length=100)
    stripe_subscription_id = models.CharField(_('Stripe Subscription ID'), max_length=100)
    plan_type = models.CharField(
        max_length=10,
        choices=PlanType.choices,
        default=PlanType.MONTHLY
    )
    is_active = models.BooleanField(_('is active'), default=True)
    current_period_start = models.DateTimeField(_('current period start'))
    current_period_end = models.DateTimeField(_('current period end'))
    cancel_at_period_end = models.BooleanField(_('cancel at period end'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.plan_type} subscription"

class RoseBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rose_balance'
    )
    balance = models.PositiveIntegerField(_('rose balance'), default=3)
    last_reset = models.DateTimeField(_('last reset'), auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username}'s rose balance: {self.balance}"

class Boost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boosts'
    )
    start_time = models.DateTimeField(_('start time'), auto_now_add=True)
    end_time = models.DateTimeField(_('end time'))
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s boost until {self.end_time}"

class InviteCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invite_codes'
    )
    code = models.CharField(_('invite code'), max_length=20, unique=True)
    is_used = models.BooleanField(_('is used'), default=False)
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_invite_codes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invite code: {self.code} by {self.user.username}" 