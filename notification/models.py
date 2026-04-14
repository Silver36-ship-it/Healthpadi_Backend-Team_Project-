from django.db import models
from django.conf import settings
from providers.models import Providers
import uuid


class Notification(models.Model):

    CHANNEL_TYPE = (
        ('email', 'Email'),
        ('sms', 'SMS'),
    )

    NOTIFICATION_TYPE = (
        ('welcome', 'Welcome'),
        ('weekly_report', 'Weekly Report'),
        ('price_submission', 'Price Submission'),
        ('general', 'General'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    provider = models.ForeignKey(
        Providers,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    message = models.TextField(blank=False)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE, default='general')
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE, default='email')
    is_read = models.BooleanField(default=False)
    reference_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.notification_type} - {self.created_at.strftime('%d %b %Y')}"

    class Meta:
        ordering = ['-created_at']