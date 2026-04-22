from django.db import models
from django.conf import settings


class ProcedureLibrary(models.Model):
    CATEGORIES = [
        ('diagnostics', 'Diagnostics & Lab Tests'),
        ('imaging', 'Imaging & Radiology'),
        ('consultation', 'Consultation'),
        ('surgery', 'Surgery & Procedures'),
        ('dental', 'Dental'),
        ('maternity', 'Maternity & Gynaecology'),
        ('pharmacy', 'Pharmacy & Drugs'),
        ('physiotherapy', 'Physiotherapy'),
        ('eye', 'Eye Care'),
        ('mental_health', 'Mental Health'),
        ('emergency', 'Emergency Care'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORIES, default='other')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    class Meta:
        verbose_name_plural = 'Procedure Library'
        ordering = ['category', 'name']


class Facilities(models.Model):
    FACILITY_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('pharmacy', 'Pharmacy'),
    ]
    DATA_SOURCES = [
        ('osm', 'OpenStreetMap'),
        ('admin', 'Admin'),
        ('provider', 'Provider'),
    ]

    facility_id = models.AutoField(primary_key=True)
    provider = models.ForeignKey(
        'providers.Providers',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='facilities'
    )
    facility_name = models.CharField(max_length=200)
    facility_address = models.CharField(max_length=300, blank=True)
    facility_city = models.CharField(max_length=100)
    facility_state = models.CharField(max_length=100)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES, default='private')

    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # NEW: Contact & hours from OSM
    phone = models.CharField(max_length=50, blank=True)
    opening_hours = models.JSONField(null=True, blank=True)

    # NEW: OSM deduplication
    osm_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    osm_synced_at = models.DateTimeField(null=True, blank=True)

    # NEW: Data source tracking
    data_source = models.CharField(max_length=20, choices=DATA_SOURCES, default='provider')

    # NEW: Claim tracking
    is_claimed = models.BooleanField(default=False)
    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='claimed_facilities'
    )

    # Verification — default False, admin must approve
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    # Legacy field — kept for compatibility
    procedures = models.TextField(default='General Consultation', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.facility_name

    @property
    def is_price_stale(self):
        """True if no procedure price updated in last 30 days."""
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return not self.pricing.filter(last_verified__gte=thirty_days_ago).exists()

    @property
    def is_truly_verified(self):
        """Meaningful verified: admin-approved AND prices updated within 30 days."""
        return self.is_verified and not self.is_price_stale

    class Meta:
        verbose_name_plural = 'Facilities'


class FacilityProcedure(models.Model):
    PRICE_SOURCES = [
        ('provider', 'Provider Official'),
        ('community', 'Community Reported'),
        ('admin', 'Admin'),
    ]

    facility = models.ForeignKey(Facilities, on_delete=models.CASCADE, related_name='pricing')
    procedure_library = models.ForeignKey(
        ProcedureLibrary,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='facility_prices'
    )
    procedure_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    # NEW: Track where the price came from
    price_source = models.CharField(max_length=20, choices=PRICE_SOURCES, default='provider')
    community_submission_count = models.IntegerField(default=0)
    last_verified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.procedure_name} at {self.facility.facility_name}"

    class Meta:
        unique_together = ('facility', 'procedure_name')
        ordering = ['procedure_name']


class PriceHistory(models.Model):
    """
    Auto-created every time a FacilityProcedure price changes.
    Powers the price history timeline on the facility detail page.
    """
    facility_procedure = models.ForeignKey(
        FacilityProcedure,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='price_changes'
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.facility_procedure.procedure_name}: ₦{self.old_price} → ₦{self.new_price}"

    class Meta:
        ordering = ['-changed_at']


class CommunityPriceSubmission(models.Model):
    """
    Price reports submitted by patients who visited a facility.
    When 3+ submissions agree within 20%, auto-promote to FacilityProcedure.
    """
    facility = models.ForeignKey(Facilities, on_delete=models.CASCADE, related_name='community_prices')
    procedure_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_submissions'
    )
    visited_on = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.procedure_name} at {self.facility.facility_name} — ₦{self.price}"

    class Meta:
        ordering = ['-created_at']


class FacilityClaim(models.Model):
    """
    A provider submitting a claim to own/manage a facility.
    Admin reviews and approves or rejects.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    facility = models.ForeignKey(Facilities, on_delete=models.CASCADE, related_name='claims')
    provider_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='facility_claims'
    )
    license_number = models.CharField(max_length=100)
    contact_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.provider_user} → {self.facility.facility_name} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        # One active claim per user per facility
        unique_together = ('facility', 'provider_user')
