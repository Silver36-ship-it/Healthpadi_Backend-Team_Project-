import csv
import io
import requests
from django.utils import timezone
from django.db.models import Q, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from facilities.models import (
    Facilities, FacilityProcedure, ProcedureLibrary,
    PriceHistory, CommunityPriceSubmission, FacilityClaim
)
from facilities.serializer import (
    FacilitiesSerializer, FacilityProcedureSerializer, ProcedureLibrarySerializer,
    PriceHistorySerializer, CommunityPriceSerializer, FacilityClaimSerializer
)


def is_provider(user):
    return user.is_authenticated and user.role == 'provider'


# ── Public Endpoints ───────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def get_facilities(request):
    """List all verified facilities. Supports filtering by city, state, type."""
    facilities = Facilities.objects.filter(
        is_verified=True, 
        facility_state__icontains='Lagos'
    ).prefetch_related('pricing')

    city = request.query_params.get('city')
    state = request.query_params.get('state')
    facility_type = request.query_params.get('type')

    if city:
        facilities = facilities.filter(facility_city__icontains=city)
    if state:
        facilities = facilities.filter(facility_state__icontains=state)
    if facility_type:
        facilities = facilities.filter(facility_type=facility_type)

    serializer = FacilitiesSerializer(facilities, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_facility_detail(request, pk):
    """Get full facility detail including pricing and price history."""
    try:
        facility = Facilities.objects.prefetch_related('pricing', 'pricing__history').get(pk=pk)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = FacilitiesSerializer(facility)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_nearby_facilities(request):
    """
    Return verified facilities near a city or lat/lng.
    Used as fallback when search finds no prices — no dead ends.
    """
    city = request.query_params.get('city', '')
    state = request.query_params.get('state', '')

    facilities = Facilities.objects.filter(
        is_verified=True, 
        facility_state__icontains='Lagos'
    )
    if city:
        facilities = facilities.filter(facility_city__icontains=city)
    if state:
        facilities = facilities.filter(facility_state__icontains=state)

    facilities = facilities[:10]
    serializer = FacilitiesSerializer(facilities, many=True)
    return Response({
        'no_prices_found': True,
        'message': 'No published prices for this procedure yet. These facilities are nearby — call them directly.',
        'facilities': serializer.data
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def facility_pricing(request, pk):
    """GET: list prices. POST: add price (provider only)."""
    try:
        facility = Facilities.objects.get(pk=pk)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        procedures = FacilityProcedure.objects.filter(facility=facility).prefetch_related('history')
        serializer = FacilityProcedureSerializer(procedures, many=True)
        return Response(serializer.data)

    if not is_provider(request.user):
        return Response({'error': 'Only providers can add pricing'}, status=status.HTTP_403_FORBIDDEN)

    serializer = FacilityProcedureSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(facility=facility, price_source='provider')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def facility_pricing_detail(request, pk, price_id):
    """Update or delete a procedure price (provider only)."""
    if not is_provider(request.user):
        return Response({'error': 'Only providers can modify pricing'}, status=status.HTTP_403_FORBIDDEN)
    try:
        procedure = FacilityProcedure.objects.get(pk=price_id, facility_id=pk)
    except FacilityProcedure.DoesNotExist:
        return Response({'error': 'Pricing not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        procedure.delete()
        return Response({'message': 'Pricing deleted'}, status=status.HTTP_204_NO_CONTENT)

    serializer = FacilityProcedureSerializer(procedure, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def facility_price_history(request, pk):
    """Get price change history for all procedures in a facility."""
    history = PriceHistory.objects.filter(
        facility_procedure__facility_id=pk
    ).select_related('facility_procedure').order_by('-changed_at')

    result = []
    for h in history:
        result.append({
            'procedure_name': h.facility_procedure.procedure_name,
            'old_price': str(h.old_price),
            'new_price': str(h.new_price),
            'direction': 'up' if h.new_price > h.old_price else 'down',
            'changed_at': h.changed_at.isoformat(),
        })
    return Response(result)


# ── Provider Endpoints ────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_facilities(request):
    """Return ONLY this provider's facilities. Never returns other providers' data."""
    if not is_provider(request.user):
        return Response({'error': 'Only providers can access this'}, status=status.HTTP_403_FORBIDDEN)

    # Facilities this user has claimed
    facilities = Facilities.objects.filter(
        claimed_by=request.user
    ).prefetch_related('pricing')

    serializer = FacilitiesSerializer(facilities, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_facility(request):
    """Provider creates a new facility. Starts as unverified (admin must approve)."""
    if not is_provider(request.user):
        return Response({'error': 'Only providers can create facilities'}, status=status.HTTP_403_FORBIDDEN)

    serializer = FacilitiesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            claimed_by=request.user,
            is_claimed=True,
            is_verified=False,
            data_source='provider'
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_facility(request, pk):
    """Provider updates their own facility."""
    if not is_provider(request.user):
        return Response({'error': 'Only providers can update facilities'}, status=status.HTTP_403_FORBIDDEN)
    try:
        facility = Facilities.objects.get(pk=pk, claimed_by=request.user)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found or not yours'}, status=status.HTTP_404_NOT_FOUND)
    serializer = FacilitiesSerializer(facility, data=request.data, partial=(request.method == 'PATCH'))
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_facility(request, pk):
    """Provider deletes their own facility."""
    if not is_provider(request.user):
        return Response({'error': 'Only providers can delete facilities'}, status=status.HTTP_403_FORBIDDEN)
    try:
        facility = Facilities.objects.get(pk=pk, claimed_by=request.user)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found or not yours'}, status=status.HTTP_404_NOT_FOUND)
    facility.delete()
    return Response({'message': 'Facility deleted'}, status=status.HTTP_204_NO_CONTENT)


# ── Facility Claim Flow ───────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def claim_facility(request, pk):
    """
    Provider claims an existing facility (from OSM or admin seed).
    Body: { license_number, contact_email }
    """
    if not is_provider(request.user):
        return Response({'error': 'Only providers can claim facilities'}, status=status.HTTP_403_FORBIDDEN)

    try:
        facility = Facilities.objects.get(pk=pk)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)

    if FacilityClaim.objects.filter(facility=facility, provider_user=request.user, status='pending').exists():
        return Response({'error': 'You already have a pending claim for this facility'}, status=status.HTTP_400_BAD_REQUEST)

    claim = FacilityClaim.objects.create(
        facility=facility,
        provider_user=request.user,
        license_number=request.data.get('license_number', ''),
        contact_email=request.data.get('contact_email', request.user.email),
    )
    serializer = FacilityClaimSerializer(claim)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_claims(request):
    """Provider sees their own claim submissions and statuses."""
    if not is_provider(request.user):
        return Response({'error': 'Only providers can view claims'}, status=status.HTTP_403_FORBIDDEN)
    claims = FacilityClaim.objects.filter(provider_user=request.user)
    serializer = FacilityClaimSerializer(claims, many=True)
    return Response(serializer.data)


# ── Community Price Submission ────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_community_price(request):
    """
    Any logged-in user can submit a community price report.
    Shown immediately as 'Community Reported'.
    When 3+ submissions within 20% variance, auto-promote to FacilityProcedure.
    """
    serializer = CommunityPriceSerializer(data=request.data)
    if serializer.is_valid():
        submission = serializer.save(submitted_by=request.user)

        # Check if we should auto-promote
        facility = submission.facility
        procedure = submission.procedure_name

        submissions = CommunityPriceSubmission.objects.filter(
            facility=facility,
            procedure_name__iexact=procedure,
        )

        if submissions.count() >= 3:
            prices = [s.price for s in submissions]
            avg_price = sum(prices) / len(prices)
            # Check within 20% variance
            in_range = all(abs(p - avg_price) / avg_price <= 0.20 for p in prices)

            if in_range:
                # Auto-promote: create or update the FacilityProcedure
                fp, created = FacilityProcedure.objects.get_or_create(
                    facility=facility,
                    procedure_name=procedure,
                    defaults={
                        'price': avg_price,
                        'price_source': 'community',
                        'community_submission_count': submissions.count(),
                    }
                )
                if not created and fp.price_source == 'community':
                    fp.price = avg_price
                    fp.community_submission_count = submissions.count()
                    fp.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def facility_community_prices(request, pk):
    """Get community-submitted prices for a facility."""
    submissions = CommunityPriceSubmission.objects.filter(facility_id=pk).order_by('-created_at')
    serializer = CommunityPriceSerializer(submissions, many=True)
    return Response(serializer.data)


# ── Admin Endpoints ───────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_facilities(request):
    """Admin: facilities awaiting approval."""
    facilities = Facilities.objects.filter(is_verified=False).prefetch_related('pricing')
    serializer = FacilitiesSerializer(facilities, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def approve_facility(request, pk):
    """Admin: approve facility → goes live in search."""
    try:
        facility = Facilities.objects.get(pk=pk)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)
    facility.is_verified = True
    facility.verified_at = timezone.now()
    facility.save()
    return Response({'message': f'{facility.facility_name} approved and now live.'})


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def reject_facility(request, pk):
    """Admin: reject/unpublish a facility."""
    try:
        facility = Facilities.objects.get(pk=pk)
    except Facilities.DoesNotExist:
        return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)
    facility.is_verified = False
    facility.verified_at = None
    facility.save()
    return Response({'message': f'{facility.facility_name} has been unpublished.'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_claims(request):
    """Admin: all pending facility claims."""
    claims = FacilityClaim.objects.filter(status='pending').select_related('facility', 'provider_user')
    serializer = FacilityClaimSerializer(claims, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def approve_claim(request, pk):
    """Admin: approve a facility claim. Links provider to facility."""
    try:
        claim = FacilityClaim.objects.get(pk=pk)
    except FacilityClaim.DoesNotExist:
        return Response({'error': 'Claim not found'}, status=status.HTTP_404_NOT_FOUND)

    claim.status = 'approved'
    claim.reviewed_at = timezone.now()
    claim.save()

    # Link the facility to the provider
    facility = claim.facility
    facility.claimed_by = claim.provider_user
    facility.is_claimed = True
    facility.is_verified = True
    facility.verified_at = timezone.now()
    facility.save()

    return Response({'message': f'Claim approved. {facility.facility_name} is now linked to {claim.provider_user.email}.'})


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def reject_claim(request, pk):
    """Admin: reject a facility claim."""
    try:
        claim = FacilityClaim.objects.get(pk=pk)
    except FacilityClaim.DoesNotExist:
        return Response({'error': 'Claim not found'}, status=status.HTTP_404_NOT_FOUND)

    claim.status = 'rejected'
    claim.reviewed_at = timezone.now()
    claim.notes = request.data.get('notes', '')
    claim.save()
    return Response({'message': 'Claim rejected.'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_create_facility(request):
    """Admin creates a facility — auto-verified."""
    serializer = FacilitiesSerializer(data=request.data)
    if serializer.is_valid():
        facility = serializer.save(
            is_verified=True,
            verified_at=timezone.now(),
            data_source='admin'
        )
        return Response(FacilitiesSerializer(facility).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def bulk_import_facilities(request):
    """Admin: upload CSV to bulk-create facilities. Required cols: facility_name, facility_city, facility_state."""
    csv_file = request.FILES.get('file')
    if not csv_file:
        return Response({'error': 'No file uploaded. Send a CSV as "file".'}, status=status.HTTP_400_BAD_REQUEST)
    if not csv_file.name.endswith('.csv'):
        return Response({'error': 'File must be a .csv'}, status=status.HTTP_400_BAD_REQUEST)

    decoded = csv_file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    required = {'facility_name', 'facility_city', 'facility_state'}
    if not required.issubset(set(reader.fieldnames or [])):
        return Response({'error': f'CSV must contain: {", ".join(required)}'}, status=status.HTTP_400_BAD_REQUEST)

    created, skipped = [], []
    for row in reader:
        name = row.get('facility_name', '').strip()
        city = row.get('facility_city', '').strip()
        state = row.get('facility_state', '').strip()
        if not name or not city or not state:
            skipped.append({'reason': 'missing fields', 'row': row})
            continue
        if Facilities.objects.filter(facility_name__iexact=name, facility_city__iexact=city).exists():
            skipped.append(name)
            continue
        Facilities.objects.create(
            facility_name=name,
            facility_address=row.get('facility_address', '').strip(),
            facility_city=city,
            facility_state=state,
            facility_type=row.get('facility_type', 'private') or 'private',
            phone=row.get('phone', '').strip(),
            latitude=row.get('latitude') or None,
            longitude=row.get('longitude') or None,
            is_verified=True,
            data_source='admin',
            verified_at=timezone.now(),
        )
        created.append(name)

    return Response({
        'message': f'{len(created)} facilities imported, {len(skipped)} skipped.',
        'created': created,
        'skipped': skipped,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def sync_from_osm(request):
    """
    Admin: sync healthcare facilities from OpenStreetMap for a Nigerian city.
    Completely free — no API key needed.
    Body: { city, state, radius_km (optional, default 50), force (optional) }
    """
    city = request.data.get('city', '').strip()
    state = request.data.get('state', 'Nigeria').strip()
    radius_km = int(request.data.get('radius_km', 50))
    force = request.data.get('force', False)

    if not city:
        return Response({'error': 'city is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Don't re-sync within 7 days unless forced
    if not force:
        from datetime import timedelta
        seven_days_ago = timezone.now() - timedelta(days=7)
        if Facilities.objects.filter(facility_city__iexact=city, data_source='osm', osm_synced_at__gte=seven_days_ago).exists():
            return Response({'message': f'{city} was synced recently. Pass force=true to re-sync.', 'skipped': True})

    # Step 1: Geocode city with Nominatim (free)
    HEADERS = {'User-Agent': 'HealthPadi/1.0 (healthpadi.ng)'}
    try:
        geo_resp = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': f'{city}, {state}', 'format': 'json', 'limit': 1},
            headers=HEADERS,
            timeout=15
        )
        geo_data = geo_resp.json()
        if not geo_data:
            return Response({'error': f'Could not find coordinates for {city}, {state}'}, status=status.HTTP_400_BAD_REQUEST)
        lat = float(geo_data[0]['lat'])
        lon = float(geo_data[0]['lon'])
    except Exception as e:
        return Response({'error': f'Geocoding failed: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)

    # Step 2: Query Overpass API for healthcare facilities
    amenities = 'hospital|clinic|pharmacy|doctors|dentist'
    query = f"""
    [out:json][timeout:60];
    (
      node["amenity"~"{amenities}"](around:{radius_km * 1000},{lat},{lon});
      way["amenity"~"{amenities}"](around:{radius_km * 1000},{lat},{lon});
    );
    out body center;
    """
    AMENITY_MAP = {'hospital': 'public', 'clinic': 'private', 'doctors': 'private', 'dentist': 'private', 'pharmacy': 'pharmacy'}

    try:
        osm_resp = requests.post(
            'https://overpass-api.de/api/interpreter',
            data={'data': query},
            headers=HEADERS,
            timeout=90
        )
        osm_resp.raise_for_status()
        elements = osm_resp.json().get('elements', [])
    except requests.exceptions.Timeout:
        return Response({'error': 'OSM request timed out. Try smaller radius.'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except Exception as e:
        return Response({'error': f'OSM request failed: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)

    # Step 3: Save to database
    created = updated = skipped = 0
    now = timezone.now()

    for el in elements:
        tags = el.get('tags', {})
        name = tags.get('name', '').strip()
        if not name:
            skipped += 1
            continue

        if el['type'] == 'node':
            f_lat, f_lon = el.get('lat'), el.get('lon')
        else:
            center = el.get('center', {})
            f_lat, f_lon = center.get('lat'), center.get('lon')

        if not f_lat or not f_lon:
            skipped += 1
            continue

        osm_id = str(el['id'])
        amenity = tags.get('amenity', '')
        facility_type = AMENITY_MAP.get(amenity, 'private')
        phone = tags.get('phone') or tags.get('contact:phone') or ''
        address_parts = filter(None, [tags.get('addr:housenumber'), tags.get('addr:street')])
        address = ', '.join(address_parts) or tags.get('addr:full', '')

        defaults = {
            'facility_name': name,
            'facility_address': address,
            'facility_city': city,
            'facility_state': state,
            'facility_type': facility_type,
            'latitude': f_lat,
            'longitude': f_lon,
            'phone': phone,
            'data_source': 'osm',
            'is_verified': True,  # OSM facilities auto-verified
            'osm_synced_at': now,
        }

        facility, was_created = Facilities.objects.get_or_create(osm_id=osm_id, defaults=defaults)
        if was_created:
            created += 1
        else:
            # Update mutable fields but preserve provider data
            facility.facility_name = name
            facility.latitude = f_lat
            facility.longitude = f_lon
            facility.phone = phone or facility.phone
            facility.osm_synced_at = now
            facility.save()
            updated += 1

    return Response({
        'city': city,
        'state': state,
        'total_found': len(elements),
        'created': created,
        'updated': updated,
        'skipped': skipped,
        'message': f'Sync complete. {created} new facilities added, {updated} updated.',
    })


# ── Procedure Library ─────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def procedure_library(request):
    """Master procedure catalogue — providers pick from this when publishing prices."""
    category = request.query_params.get('category')
    search = request.query_params.get('q')

    procedures = ProcedureLibrary.objects.filter(is_active=True)
    if category:
        procedures = procedures.filter(category=category)
    if search:
        procedures = procedures.filter(name__icontains=search)

    serializer = ProcedureLibrarySerializer(procedures, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_procedure_to_library(request):
    """Admin: add a new procedure to the master catalogue."""
    serializer = ProcedureLibrarySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
