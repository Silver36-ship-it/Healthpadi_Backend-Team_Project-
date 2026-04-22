import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthpadi.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import sys

print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")

try:
    send_mail(
        subject="HealthPadi SMTP Test",
        message="If you receive this, your SMTP configuration is working perfectly!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER], # Send it to themselves
        fail_silently=False, # We want to see the error!
    )
    print("SUCCESS: Test email sent!")
except Exception as e:
    print(f"FAILED TO SEND EMAIL: {type(e).__name__}: {e}")
    sys.exit(1)
