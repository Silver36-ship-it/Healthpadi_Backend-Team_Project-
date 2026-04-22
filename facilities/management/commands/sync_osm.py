import random
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from facilities.models import Facilities, FacilityProcedure

class Command(BaseCommand):
    help = 'Sync healthcare facilities from OpenStreetMap and seed mock procedures/prices'

    def add_arguments(self, parser):
        parser.add_argument('city', type=str, help='City to search in, e.g. "Lagos"')
        parser.add_argument('--state', type=str, default='Nigeria', help='State/Country to improve geocoding')
        parser.add_argument('--radius', type=int, default=50, help='Radius in km (default 50)')

    def handle(self, *args, **options):
        city = options['city']
        state = options['state']
        radius_km = options['radius']

        self.stdout.write(f"Geocoding {city}, {state}...")
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
                self.stderr.write(self.style.ERROR(f'Could not find coordinates for {city}, {state}'))
                return
            lat = float(geo_data[0]['lat'])
            lon = float(geo_data[0]['lon'])
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Geocoding failed: {str(e)}'))
            return

        self.stdout.write(f"Found coordinates: {lat}, {lon}. Querying Overpass API...")
        
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
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'OSM request failed: {str(e)}'))
            return

        self.stdout.write(f"Found {len(elements)} elements. Saving to database and seeding prices...")

        created = updated = skipped = 0
        now = timezone.now()

        procedure_prices = {
            "Surgery": (250000, 1200000),
            "Dental Care": (15000, 150000),
            "Kidney Transplant": (12000000, 18000000),
            "General Surgery": (150000, 750000),
            "Cardiology": (50000, 350000),
            "Orthopedics": (80000, 950000),
            "Physical Therapy": (10000, 45000),
            "Intensive Care": (25000, 150000),
            "Pediatrics": (10000, 75000),
            "Neurology": (45000, 250000),
            "Maternity": (100000, 1200000),
            "X-Ray": (8000, 25000),
            "Scan": (15000, 45000),
            "Eye Care": (15000, 120000),
            "Laboratory": (5000, 85000),
            "General Consultation": (5000, 25000)
        }

        procedure_keys = list(procedure_prices.keys())
        price_sources = ['provider', 'community', 'admin']

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
                'is_verified': True,
                'osm_synced_at': now,
            }

            facility, was_created = Facilities.objects.get_or_create(osm_id=osm_id, defaults=defaults)
            if was_created:
                created += 1
            else:
                facility.facility_name = name
                facility.latitude = f_lat
                facility.longitude = f_lon
                facility.phone = phone or facility.phone
                facility.osm_synced_at = now
                facility.save()
                updated += 1
            
            # Seed 2-5 random procedures for this facility
            procedures_to_add = random.sample(procedure_keys, random.randint(2, 5))
            for p_name in procedures_to_add:
                price_range = procedure_prices[p_name]
                price = random.randint(price_range[0], price_range[1])
                source = random.choice(price_sources)
                
                fp, fp_created = FacilityProcedure.objects.get_or_create(
                    facility=facility,
                    procedure_name=p_name,
                    defaults={'price': price, 'price_source': source}
                )
                if not fp_created:
                    pass

        self.stdout.write(self.style.SUCCESS(f'Sync complete. {created} new facilities added, {updated} updated, {skipped} skipped.'))
