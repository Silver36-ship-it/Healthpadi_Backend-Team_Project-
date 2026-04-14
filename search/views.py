from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from providers.models import Providers
from providers.serializers import ProviderSerializer
from facilities.models import Facilities
from facilities.serializer import FacilitiesSerializer
from django.db.models import Q

@api_view(['GET'])
@permission_classes([AllowAny])
def global_search(request):
    """
    Search across providers and facilities using a single query string.
    """
    query = request.query_params.get('q', '')
    
    if not query:
        return Response({
            "providers": [],
            "facilities": []
        })

    # Search Providers
    providers = Providers.objects.filter(
        Q(provider_name__icontains=query) | 
        Q(provider_city__icontains=query) |
        Q(provider_type__icontains=query)
    ).filter(is_verified=True)
    
    # Search Facilities
    facilities = Facilities.objects.filter(
        Q(facility_name__icontains=query) |
        Q(facility_city__icontains=query) |
        Q(facility_address__icontains=query)
    ).filter(is_verified=True)

    provider_serializer = ProviderSerializer(providers, many=True)
    facility_serializer = FacilitiesSerializer(facilities, many=True)

    return Response({
        "providers": provider_serializer.data,
        "facilities": facility_serializer.data
    })
