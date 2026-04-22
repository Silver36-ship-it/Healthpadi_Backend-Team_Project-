from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLES = [('user','User'),('provider','Provider')]
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)