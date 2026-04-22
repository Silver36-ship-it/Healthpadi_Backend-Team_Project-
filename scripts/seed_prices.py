"""
Seed each hospital with a realistic selection of procedures and random prices.
Uses the ProcedureLibrary as the source of procedure names.
Run: uv run python scripts/seed_prices.py
"""
import os
import sys
import django
import random

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthpadi.settings')
django.setup()

from facilities.models import Facilities, FacilityProcedure, ProcedureLibrary

# Price ranges per category (in Naira)
CATEGORY_PRICE_RANGES = {
    'diagnostics': (2000, 45000),
    'imaging': (8000, 350000),
    'consultation': (3000, 25000),
    'surgery': (80000, 1500000),
    'dental': (5000, 150000),
    'maternity': (15000, 800000),
    'pharmacy': (500, 15000),
    'physiotherapy': (5000, 35000),
    'eye': (5000, 500000),
    'mental_health': (5000, 50000),
    'emergency': (10000, 150000),
    'other': (3000, 50000),
}

hospitals = Facilities.objects.all()
all_procedures = list(ProcedureLibrary.objects.filter(is_active=True))

if not all_procedures:
    print("ERROR: No procedures in ProcedureLibrary. Run seed_data.py first!")
    sys.exit(1)

total_created = 0
for h in hospitals:
    # Each hospital gets 8-20 random procedures from the library
    num_procs = random.randint(8, min(20, len(all_procedures)))
    selected = random.sample(all_procedures, num_procs)

    for proc in selected:
        price_range = CATEGORY_PRICE_RANGES.get(proc.category, (5000, 50000))
        # Round to nearest 500 for realism
        price = round(random.randint(price_range[0], price_range[1]) / 500) * 500

        _, created = FacilityProcedure.objects.get_or_create(
            facility=h,
            procedure_name=proc.name,
            defaults={
                'price': price,
                'procedure_library': proc,
                'price_source': random.choice(['provider', 'community', 'admin']),
            }
        )
        if created:
            total_created += 1

print(f"Seeded {total_created} procedure prices across {hospitals.count()} hospitals.")
print(f"Total FacilityProcedure entries now: {FacilityProcedure.objects.count()}")
