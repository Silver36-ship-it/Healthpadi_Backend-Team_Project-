from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    price_difference = serializers.ReadOnlyField()
    is_overcharged = serializers.ReadOnlyField()
    user_name = serializers.CharField(
        source='user.username',
        read_only=True
    )
    facility_name = serializers.CharField(
        source='facility.facility_name',
        read_only=True
    )

    class Meta:
        model = Report
        fields = [
            'id',
            'user',
            'user_name',
            'facility',
            'facility_name',
            'procedure',
            'advertised_price',
            'charged_price',
            'price_difference',
            'is_overcharged',
            'status',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'created_at'
        ]

