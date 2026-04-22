import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthpadi.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print(f"Testing SMTP to a different email address...")
print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"From: {settings.DEFAULT_FROM_EMAIL}")

# Use a test email (e.g. a fake one)
test_email = "test_user_healthpadi_1234@mailinator.com"

try:
    send_mail(
        subject="Welcome to HealthPadi! (Test)",
        message="This is a test to a different email address.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[test_email],
        fail_silently=False,
    )
    print(f"SUCCESS: Email successfully accepted by SMTP server for {test_email}!")
except Exception as e:
    print(f"FAILED TO SEND EMAIL: {type(e).__name__}: {e}")
    sys.exit(1)
