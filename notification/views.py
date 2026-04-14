from datetime import timezone, timedelta

from django.core.mail import send_mail
from django.shortcuts import render

from notification.models import Notification
from providers.models import Providers


# Create your views here.


def create_user_notification(user):
    notification = Notification.objects.create(
        message=f"""
        We are glad to have you here {user.first_name} {user.last_name}!\n   
        Welcome to HealthPadi!   
        """,
    )
    send_mail(
        subject="Welcome to HealthPadi!",
        message=notification.message,
        from_email='',
        recipient_list=[user.email],
        fail_silently=True
    )
    notification.is_read = True
    notification.save()

def create_provider_notification(provider):
    notification = Notification.objects.create(
        message=f"""
        Dear {provider.provider_name}, We are glad to partner with you!
        
        Welcome to HealthPadi!   
        """,
    )
    send_mail(
        subject="Welcome to HealthPadi Partner!",
        message=notification.message,
        from_email='',
        recipient_list=[provider.provider_email],
        fail_silently=True
    )
    notification.is_read = True
    notification.save()

def create_notification_for_provider_views(provider, view_count):
    today = timezone.now()
    week_start = today - timedelta(days=7)

    notification = Notification.objects.create(
        message=f"""
        Hello {provider.provider_name}, here is your weekly summary on HealthPadi!

        This week's report ({week_start.strftime('%d %b')} - {today.strftime('%d %b %Y')}):

        - Patients who viewed your facility this week: {view_count}

        Keep your price listings up to date to attract more patients.

        Thank you for partnering with HealthPadi!
        """,
    )
    send_mail(
        subject=f"Your Weekly HealthPadi Report — {today.strftime('%d %b %Y')}",
        message=notification.message,
        from_email='',
        recipient_list=[provider.provider_email],
        fail_silently=True
    )
    notification.is_read = False
    notification.save()


