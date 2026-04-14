from rest_framework import serializers
from .models import Facilities, FacilityProcedure

class FacilityProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityProcedure
        fields = ['procedure_name', 'price', 'last_verified']

class FacilitiesSerializer(serializers.ModelSerializer):
    pricing = FacilityProcedureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Facilities
        fields = '__all__'
