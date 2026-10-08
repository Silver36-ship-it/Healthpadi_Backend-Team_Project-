from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import (
    Facilities, FacilityProcedure, ProcedureLibrary,
    PriceHistory, CommunityPriceSubmission, FacilityClaim
)


class ProcedureLibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureLibrary
        fields = ['id', 'name', 'category', 'description', 'is_active']


class PriceHistorySerializer(serializers.ModelSerializer):
    direction = serializers.SerializerMethodField()

    class Meta:
        model = PriceHistory
        fields = ['id', 'old_price', 'new_price', 'direction', 'changed_at']

    def get_direction(self, obj):
        if obj.new_price > obj.old_price:
            return 'up'
        elif obj.new_price < obj.old_price:
            return 'down'
        return 'unchanged'


class FacilityProcedureSerializer(serializers.ModelSerializer):
    history = PriceHistorySerializer(many=True, read_only=True)
    price_source_display = serializers.CharField(source='get_price_source_display', read_only=True)

    class Meta:
        model = FacilityProcedure
        fields = [
            'id', 'procedure_name', 'price', 'price_source',
            'price_source_display', 'community_submission_count',
            'last_verified', 'procedure_library', 'history'
        ]


class FacilitiesSerializer(serializers.ModelSerializer):
    pricing = FacilityProcedureSerializer(many=True, read_only=True)
    is_truly_verified = serializers.SerializerMethodField()
    is_price_stale = serializers.SerializerMethodField()
    days_since_update = serializers.SerializerMethodField()

    class Meta:
        model = Facilities
        fields = '__all__'

    def get_days_since_update(self, obj):
        latest = self._latest_price_update(obj)
        if not latest:
            return None
        delta = timezone.now() - latest
        return delta.days

    def get_is_price_stale(self, obj):
        latest = self._latest_price_update(obj)
        return latest is None or latest < timezone.now() - timedelta(days=30)

    def get_is_truly_verified(self, obj):
        return obj.is_verified and not self.get_is_price_stale(obj)

    @staticmethod
    def _latest_price_update(obj):
        return max(
            (procedure.last_verified for procedure in obj.pricing.all()),
            default=None,
        )


class CommunityPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPriceSubmission
        fields = ['id', 'facility', 'procedure_name', 'price', 'visited_on', 'created_at']
        read_only_fields = ['id', 'created_at']


class FacilityClaimSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source='facility.facility_name', read_only=True)
    facility_city = serializers.CharField(source='facility.facility_city', read_only=True)
    provider_email = serializers.EmailField(source='provider_user.email', read_only=True)

    class Meta:
        model = FacilityClaim
        fields = [
            'id', 'facility', 'facility_name', 'facility_city',
            'provider_user', 'provider_email',
            'license_number', 'contact_email', 'status', 'notes',
            'created_at', 'reviewed_at'
        ]
        read_only_fields = ['id', 'status', 'provider_user', 'created_at', 'reviewed_at']
