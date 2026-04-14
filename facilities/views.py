from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from facilities.models import Facilities
from facilities.serializer import FacilitiesSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_facility(request):
    serializer = FacilitiesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_facility(request, pk):
    try:
        facility = Facilities.objects.get(pk=pk)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=404)
    serializer = FacilitiesSerializer(facility, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_facility_detail(request, pk):
    try:
        facility = Facilities.objects.get(pk=pk, is_verified=True)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=404)
    serializer = FacilitiesSerializer(facility)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_facilities(request):
    facilities = Facilities.objects.filter(is_verified=True)

    city = request.query_params.get('city')
    provider_type = request.query_params.get('type')

    if city:
        facilities = facilities.filter(facility_city__icontains=city)
    if provider_type:
        facilities = facilities.filter(provider_type=provider_type)

    serializer = FacilitiesSerializer(facilities, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_facility(request, pk):
    try:
        facility = Facilities.objects.get(pk=pk)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=404)
    facility.delete()
    return Response({'message': 'Facility deleted successfully'}, status=204)