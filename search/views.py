from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from facilities.models import Facilities, FacilityProcedure
from facilities.serializer import FacilitiesSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def global_search(request):
    """
    Core search endpoint.
    Params: q (required), city, state
    Returns:
      - results: procedure+price matches (the core feature)
      - facilities: facility name matches
      - no_prices_found: true if zero price results (trigger fallback in frontend)
    """
    query = request.query_params.get('q', '').strip()
    city = request.query_params.get('city', '').strip()
    state = request.query_params.get('state', '').strip()

    if not query:
        return Response({'query': '', 'results': [], 'facilities': [], 'no_prices_found': False})

    # 1. Search procedure prices
    keywords = [k for k in query.split() if len(k) > 1]
    if not keywords:
        keywords = [query]

    # Start with verified facilities in Lagos
    procedure_matches = FacilityProcedure.objects.filter(
        facility__is_verified=True,
        facility__facility_state__icontains='Lagos'
    ).select_related('facility')

    # Known Lagos areas for smart location detection
    LAGOS_AREAS = [
        'ikeja', 'lekki', 'victoria island', 'vi', 'surulere', 'yaba',
        'apapa', 'ikoyi', 'ajah', 'lagos island', 'festac', 'ojota',
        'oshodi', 'mushin', 'agege', 'alimosho', 'ikorodu', 'epe',
        'badagry', 'somolu', 'bariga', 'gbagada', 'maryland', 'ojodu',
        'ogba', 'magodo', 'idi-araba', 'isolo', 'amuwo-odofin',
    ]

    # Separate location keywords from procedure keywords
    location_keywords = []
    procedure_keywords = []
    # Check for multi-word area names first (e.g., "victoria island")
    query_lower = ' '.join(keywords).lower()
    remaining_keywords = list(keywords)
    for area in sorted(LAGOS_AREAS, key=len, reverse=True):  # longest first
        if area in query_lower:
            location_keywords.append(area)
            # Remove matched area words from remaining keywords
            area_words = area.split()
            for aw in area_words:
                for rk in remaining_keywords[:]:
                    if rk.lower() == aw:
                        remaining_keywords.remove(rk)
                        break
            query_lower = query_lower.replace(area, '').strip()

    # Anything left is a procedure keyword
    procedure_keywords = [k for k in remaining_keywords if len(k) > 1]

    # Apply procedure keyword matching (strict AND first)
    strict_matches = procedure_matches
    for kw in procedure_keywords:
        strict_matches = strict_matches.filter(
            Q(procedure_name__icontains=kw) |
            Q(facility__facility_name__icontains=kw)
        )

    # Apply location filtering
    if location_keywords:
        loc_q = Q()
        for loc in location_keywords:
            loc_q |= Q(facility__facility_address__icontains=loc)
        strict_matches = strict_matches.filter(loc_q)

    # If strict AND returns zero results and we have 2+ procedure keywords,
    # fall back to OR matching (any keyword matches)
    if not strict_matches.exists() and len(procedure_keywords) >= 2:
        relaxed_q = Q()
        for kw in procedure_keywords:
            relaxed_q |= Q(procedure_name__icontains=kw)
        procedure_matches = procedure_matches.filter(relaxed_q)
        if location_keywords:
            loc_q = Q()
            for loc in location_keywords:
                loc_q |= Q(facility__facility_address__icontains=loc)
            procedure_matches = procedure_matches.filter(loc_q)
    else:
        procedure_matches = strict_matches

    if city:
        procedure_matches = procedure_matches.filter(facility__facility_city__icontains=city)
    if state:
        procedure_matches = procedure_matches.filter(facility__facility_state__icontains=state)

    results = []
    for pm in procedure_matches:
        fac = pm.facility
        results.append({
            'facility_id': fac.facility_id,
            'facility_name': fac.facility_name,
            'facility_city': fac.facility_city,
            'facility_state': fac.facility_state,
            'facility_type': fac.facility_type,
            'facility_address': fac.facility_address,
            'latitude': str(fac.latitude) if fac.latitude else None,
            'longitude': str(fac.longitude) if fac.longitude else None,
            'phone': fac.phone,
            'procedure_name': pm.procedure_name,
            'price': str(pm.price),
            'price_source': pm.price_source,
            'community_submission_count': pm.community_submission_count,
            'last_verified': pm.last_verified.isoformat() if pm.last_verified else None,
            'is_truly_verified': fac.is_truly_verified,
            'is_price_stale': fac.is_price_stale,
        })

    # 2. Facility name matches (secondary)
    facility_qs = Facilities.objects.filter(
        Q(facility_name__icontains=query) | Q(facility_city__icontains=query),
        is_verified=True,
        facility_state__icontains='Lagos'
    )
    if city:
        facility_qs = facility_qs.filter(facility_city__icontains=city)
    if state:
        facility_qs = facility_qs.filter(facility_state__icontains=state)

    facilities_data = FacilitiesSerializer(facility_qs[:10], many=True).data

    # 3. No dead end — if zero price results, return nearby facilities as fallback
    fallback = []
    no_prices_found = len(results) == 0

    if no_prices_found:
        fallback_qs = Facilities.objects.filter(
            is_verified=True, 
            facility_state__icontains='Lagos'
        )
        if city:
            fallback_qs = fallback_qs.filter(facility_city__icontains=city)
        elif state:
            fallback_qs = fallback_qs.filter(facility_state__icontains=state)
        fallback = FacilitiesSerializer(fallback_qs[:10], many=True).data

    return Response({
        'query': query,
        'results': results,
        'facilities': facilities_data,
        'no_prices_found': no_prices_found,
        'fallback_facilities': fallback,
        'fallback_message': (
            f'No published prices for "{query}" yet. '
            'These nearby facilities may offer it — call them directly.'
        ) if no_prices_found else None,
    })
