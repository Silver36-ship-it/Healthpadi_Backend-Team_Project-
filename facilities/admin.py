from django.contrib import admin
from .models import (
    Facilities, FacilityProcedure, ProcedureLibrary,
    PriceHistory, CommunityPriceSubmission, FacilityClaim
)


@admin.register(ProcedureLibrary)
class ProcedureLibraryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']


class FacilityProcedureInline(admin.TabularInline):
    model = FacilityProcedure
    extra = 0


@admin.register(Facilities)
class FacilitiesAdmin(admin.ModelAdmin):
    list_display = ['facility_name', 'facility_city', 'facility_state', 'facility_type', 'is_verified', 'is_claimed', 'data_source']
    list_filter = ['is_verified', 'is_claimed', 'facility_type', 'data_source', 'facility_state']
    search_fields = ['facility_name', 'facility_city']
    inlines = [FacilityProcedureInline]
    actions = ['approve_facilities']

    def approve_facilities(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, verified_at=timezone.now())
    approve_facilities.short_description = 'Approve selected facilities'


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['facility_procedure', 'old_price', 'new_price', 'changed_at']
    readonly_fields = ['changed_at']


@admin.register(CommunityPriceSubmission)
class CommunityPriceAdmin(admin.ModelAdmin):
    list_display = ['facility', 'procedure_name', 'price', 'submitted_by', 'created_at', 'is_verified']
    list_filter = ['is_verified']


@admin.register(FacilityClaim)
class FacilityClaimAdmin(admin.ModelAdmin):
    list_display = ['facility', 'provider_user', 'status', 'created_at']
    list_filter = ['status']
    actions = ['approve_claims']

    def approve_claims(self, request, queryset):
        from django.utils import timezone
        for claim in queryset.filter(status='pending'):
            claim.status = 'approved'
            claim.reviewed_at = timezone.now()
            claim.save()
            facility = claim.facility
            facility.claimed_by = claim.provider_user
            facility.is_claimed = True
            facility.is_verified = True
            facility.save()
    approve_claims.short_description = 'Approve selected claims'
