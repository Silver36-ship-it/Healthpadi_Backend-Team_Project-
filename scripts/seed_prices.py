import os
import sys
import django
import random

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthpadi.test_settings')
django.setup()

from facilities.models import Facilities, FacilityProcedure

hospitals = Facilities.objects.all()

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

for h in hospitals:
    procs = h.procedures.split(',')
    for p_name in procs:
        p_name = p_name.strip()
        price_range = procedure_prices.get(p_name, (5000, 50000))
        price = random.randint(price_range[0], price_range[1])
        
        FacilityProcedure.objects.get_or_create(
            facility=h,
            procedure_name=p_name,
            defaults={'price': price}
        )

print(f"Successfully seeded procedure prices for {len(hospitals)} hospitals.")
