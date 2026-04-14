import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthpadi.test_settings')
django.setup()

from facilities.models import Facilities

hospitals = [
    {
        "name": "St. Nicholas Hospital",
        "city": "Lagos Island",
        "address": "57 Campbell Street",
        "procedures": "Kidney Transplant, General Surgery, Cardiology",
        "rating": 4.8,
        "lat": 6.4526,
        "lng": 3.3934
    },
    {
        "name": "Lagoon Hospital",
        "city": "Ikoyi",
        "address": "11A Idejo St, Victoria Island",
        "procedures": "Dental Care, Orthopedics, Physical Therapy",
        "rating": 4.5,
        "lat": 6.4475,
        "lng": 3.4217
    },
    {
        "name": "Reddington Hospital",
        "city": "Ikeja",
        "address": "12 Isaac John St, Ikeja",
        "procedures": "Intensive Care, Pediatrics, Neurology",
        "rating": 4.7,
        "lat": 6.5910,
        "lng": 3.3592
    },
    {
        "name": "Evercare Hospital Lekki",
        "city": "Lekki",
        "address": "16 Admiralty Way",
        "procedures": "Maternity, X-Ray, Scan, Surgery",
        "rating": 4.6,
        "lat": 6.4439,
        "lng": 3.4839
    },
    {
        "name": "Eko Hospital",
        "city": "Ikeja",
        "address": "31 Mobolaji Bank Anthony Way",
        "procedures": "General Consultation, Eye Care, Laboratory",
        "rating": 4.2,
        "lat": 6.5872,
        "lng": 3.3582
    }
]

for h in hospitals:
    Facilities.objects.update_or_create(
        facility_name=h['name'],
        defaults={
            'facility_city': h['city'],
            'facility_address': h['address'],
            'facility_state': 'Lagos',
            'facility_type': 'private',
            'procedures': h['procedures'],
            'rating': h['rating'],
            'latitude': h['lat'],
            'longitude': h['lng'],
            'is_verified': True
        }
    )

print(f"Successfully updated {len(hospitals)} Lagos hospitals with accurate GPS coordinates.")
