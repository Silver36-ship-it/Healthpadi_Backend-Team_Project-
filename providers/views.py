from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Providers
from .serializers import ProviderSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def provider_list(request):
    providers = Providers.objects.filter(is_verified=True)

    city = request.query_params.get('city')
    provider_type = request.query_params.get('type')

    if city:
        providers = providers.filter(provider_city__icontains=city)
    if provider_type:
        providers = providers.filter(provider_type=provider_type)

    serializer = ProviderSerializer(providers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def provider_detail(request, pk):
    try:
        provider = Providers.objects.get(pk=pk, is_verified=True)
    except Providers.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProviderSerializer(provider)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def provider_create(request):
    serializer = ProviderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def provider_update(request, pk):
    try:
        provider = Providers.objects.get(pk=pk)
    except Providers.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProviderSerializer(provider, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def provider_delete(request, pk):
    try:
        provider = Providers.objects.get(pk=pk)
    except Providers.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)

    provider.delete()
    return Response({'message': 'Provider deleted successfully'}, status=status.HTTP_204_NO_CONTENT)