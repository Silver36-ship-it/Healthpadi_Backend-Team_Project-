import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthpadi.settings')
django.setup()

from django.core import mail
from user.models import User

# Make sure we use locmem to capture emails
from django.conf import settings
settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

def test():
    # clear outbox
    mail.outbox = []
    
    email = "testnewuser@healthpadi.com"
    # remove user if exists
    User.objects.filter(email=email).delete()
    
    # create new user
    print("Creating new user...")
    user = User.objects.create_user(
        username="testnewuser",
        email=email,
        password="SecurePassword123!",
        first_name="Test",
        last_name="NewUser"
    )
    
    print(f"Emails in outbox: {len(mail.outbox)}")
    if len(mail.outbox) > 0:
        email_msg = mail.outbox[0]
        print(f"Subject: {email_msg.subject}")
        print(f"To: {email_msg.to}")
        print(f"Body: {email_msg.body}")
    else:
        print("NO EMAIL SENT")

if __name__ == '__main__':
    test()
