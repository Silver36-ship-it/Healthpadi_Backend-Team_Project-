
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from notification.views import create_user_notification

@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        create_user_notification(instance)