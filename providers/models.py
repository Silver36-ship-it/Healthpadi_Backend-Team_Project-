from django.db import models


class Providers(models.Model):
    provider_id = models.AutoField(primary_key=True)
    provider_name = models.CharField(max_length=100, blank=False)
    provider_address = models.CharField(max_length=100, blank=False)
    provider_city = models.CharField(max_length=100, blank=False)
    provider_state = models.CharField(max_length=100, blank=False)


    provider_phone = models.CharField(max_length=20, blank=True)
    provider_email = models.EmailField(blank=True)

    FACILITY_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    provider_type = models.CharField(max_length=20, choices=FACILITY_TYPES, default='private')

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    license_number = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.provider_name

    class Meta:
        verbose_name_plural = 'Providers'


