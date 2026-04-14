from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Providers
from notification.views import create_provider_notification

@receiver(post_save, sender=Providers)
def provider_created(sender, instance, created, **kwargs):
    if created:
        create_provider_notification(instance)