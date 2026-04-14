from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from facilities.models import Facilities

class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    facility = models.ForeignKey(Facilities, on_delete=models.CASCADE, related_name='reports')
    procedure = models.CharField(max_length=255)
    advertised_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    charged_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} reported {self.procedure} at {self.facility}"

    def review(self):
        self.status = 'reviewed'
        self.save()

    def resolve(self):
        self.status = 'resolved'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    @property
    def price_difference(self):
        return self.charged_price - self.advertised_price

    @property
    def is_overcharged(self):
        return self.charged_price > self.advertised_price