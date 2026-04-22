"""
HealthPadi Seed Script
Run with: uv run python scripts/seed_data.py

Seeds:
1. Procedure library (100+ standardized Nigerian medical procedures)
2. Sample Nigerian hospitals (pre-verified, for testing)
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthpadi.settings')
django.setup()

from facilities.models import Facilities, ProcedureLibrary
from django.utils import timezone

# ── 1. Procedure Library ──────────────────────────────────────────────────────
PROCEDURES = [
    ('Malaria Rapid Test (RDT)', 'diagnostics'),
    ('Malaria Blood Smear', 'diagnostics'),
    ('Full Blood Count (FBC)', 'diagnostics'),
    ('Blood Group & Genotype', 'diagnostics'),
    ('HIV Test', 'diagnostics'),
    ('Hepatitis B Surface Antigen (HBsAg)', 'diagnostics'),
    ('Hepatitis C Antibody Test', 'diagnostics'),
    ('Fasting Blood Sugar (FBS)', 'diagnostics'),
    ('Random Blood Sugar (RBS)', 'diagnostics'),
    ('HbA1c (Diabetes Monitoring)', 'diagnostics'),
    ('Urine Analysis (Urinalysis)', 'diagnostics'),
    ('Kidney Function Test (KFT)', 'diagnostics'),
    ('Liver Function Test (LFT)', 'diagnostics'),
    ('Lipid Profile', 'diagnostics'),
    ('Thyroid Function Test (TFT)', 'diagnostics'),
    ('Prostate Specific Antigen (PSA)', 'diagnostics'),
    ('Pregnancy Test (Urine)', 'diagnostics'),
    ('Widal Test (Typhoid)', 'diagnostics'),
    ('Stool Analysis', 'diagnostics'),
    ('Sputum AFB (TB Test)', 'diagnostics'),
    ('COVID-19 Rapid Antigen Test', 'diagnostics'),
    ('ESR (Erythrocyte Sedimentation Rate)', 'diagnostics'),
    ('CRP (C-Reactive Protein)', 'diagnostics'),
    ('Electrolytes (Na, K, Cl, HCO3)', 'diagnostics'),
    ('Blood Culture & Sensitivity', 'diagnostics'),
    ('Sickle Cell Screening', 'diagnostics'),
    ('Chest X-Ray', 'imaging'),
    ('Abdominal X-Ray', 'imaging'),
    ('Pelvic X-Ray', 'imaging'),
    ('Abdominal Ultrasound', 'imaging'),
    ('Pelvic Ultrasound', 'imaging'),
    ('Obstetric Ultrasound (Antenatal Scan)', 'imaging'),
    ('Breast Ultrasound', 'imaging'),
    ('Thyroid Ultrasound', 'imaging'),
    ('Prostate Ultrasound', 'imaging'),
    ('CT Scan (Head)', 'imaging'),
    ('CT Scan (Chest)', 'imaging'),
    ('CT Scan (Abdomen & Pelvis)', 'imaging'),
    ('MRI (Brain)', 'imaging'),
    ('MRI (Spine)', 'imaging'),
    ('Echocardiogram', 'imaging'),
    ('Mammogram', 'imaging'),
    ('General Consultation (OPD)', 'consultation'),
    ('Specialist Consultation', 'consultation'),
    ('Paediatric Consultation', 'consultation'),
    ('Gynaecology Consultation', 'consultation'),
    ('Cardiology Consultation', 'consultation'),
    ('Neurology Consultation', 'consultation'),
    ('Orthopaedic Consultation', 'consultation'),
    ('Dermatology Consultation', 'consultation'),
    ('ENT Consultation', 'consultation'),
    ('Appendectomy', 'surgery'),
    ('Hernia Repair', 'surgery'),
    ('Caesarean Section (C-Section)', 'surgery'),
    ('Normal Delivery (SVD)', 'surgery'),
    ('Fibroid Surgery (Myomectomy)', 'surgery'),
    ('Circumcision (Adult)', 'surgery'),
    ('Circumcision (Paediatric)', 'surgery'),
    ('Wound Dressing', 'surgery'),
    ('Suturing (Wound Closure)', 'surgery'),
    ('Blood Transfusion', 'surgery'),
    ('Dialysis (Haemodialysis)', 'surgery'),
    ('ECG (Electrocardiogram)', 'surgery'),
    ('Dental Consultation', 'dental'),
    ('Tooth Extraction (Simple)', 'dental'),
    ('Tooth Extraction (Surgical)', 'dental'),
    ('Dental Filling', 'dental'),
    ('Root Canal Treatment', 'dental'),
    ('Scaling & Polishing', 'dental'),
    ('Dental X-Ray', 'dental'),
    ('Antenatal Registration', 'maternity'),
    ('Antenatal Visit (ANC)', 'maternity'),
    ('Postnatal Visit (PNC)', 'maternity'),
    ('Family Planning Consultation', 'maternity'),
    ('IUD Insertion', 'maternity'),
    ('Pap Smear (Cervical Cancer Screening)', 'maternity'),
    ('Eye Consultation', 'eye'),
    ('Visual Acuity Test', 'eye'),
    ('Cataract Surgery', 'eye'),
    ('Glaucoma Screening', 'eye'),
    ('Physiotherapy Consultation', 'physiotherapy'),
    ('Physiotherapy Session', 'physiotherapy'),
    ('Psychiatry Consultation', 'mental_health'),
    ('Counselling Session', 'mental_health'),
    ('Emergency Consultation', 'emergency'),
    ('Ambulance Service', 'emergency'),
    ('Yellow Fever Vaccination', 'other'),
    ('Meningitis Vaccination', 'other'),
    ('Tetanus Toxoid Injection', 'other'),
    ('Hepatitis B Vaccination', 'other'),
]

print("Seeding procedure library...")
created = 0
for name, category in PROCEDURES:
    _, was_created = ProcedureLibrary.objects.get_or_create(
        name=name, defaults={'category': category, 'is_active': True}
    )
    if was_created:
        created += 1
print(f"  [OK] {created} new procedures added ({len(PROCEDURES) - created} already existed)")


# ── 2. Sample Hospitals ───────────────────────────────────────────────────────
HOSPITALS = [
    {'facility_name': 'Lagos University Teaching Hospital (LUTH)', 'facility_city': 'Lagos', 'facility_state': 'Lagos', 'facility_type': 'public', 'facility_address': 'Idi-Araba, Surulere'},
    {'facility_name': 'Lagos Island General Hospital', 'facility_city': 'Lagos', 'facility_state': 'Lagos', 'facility_type': 'public', 'facility_address': 'Lagos Island'},
    {'facility_name': 'Reddington Hospital', 'facility_city': 'Lagos', 'facility_state': 'Lagos', 'facility_type': 'private', 'facility_address': 'Victoria Island'},
    {'facility_name': 'Eko Hospital', 'facility_city': 'Lagos', 'facility_state': 'Lagos', 'facility_type': 'private', 'facility_address': 'Ikeja'},
    {'facility_name': 'Lagoon Hospital', 'facility_city': 'Lagos', 'facility_state': 'Lagos', 'facility_type': 'private', 'facility_address': 'Apapa'},
    {'facility_name': 'Evercare Hospital Lagos', 'facility_city': 'Lagos', 'facility_state': 'Lagos', 'facility_type': 'private', 'facility_address': 'Lekki'},
    {'facility_name': 'National Hospital Abuja', 'facility_city': 'Abuja', 'facility_state': 'FCT', 'facility_type': 'public', 'facility_address': 'Central Business District'},
    {'facility_name': 'University of Abuja Teaching Hospital', 'facility_city': 'Abuja', 'facility_state': 'FCT', 'facility_type': 'public', 'facility_address': 'Gwagwalada'},
    {'facility_name': 'Cedarcrest Hospital Abuja', 'facility_city': 'Abuja', 'facility_state': 'FCT', 'facility_type': 'private', 'facility_address': 'Abuja'},
    {'facility_name': 'Nizamiye Hospital', 'facility_city': 'Abuja', 'facility_state': 'FCT', 'facility_type': 'private', 'facility_address': 'Abuja'},
    {'facility_name': 'Aminu Kano Teaching Hospital', 'facility_city': 'Kano', 'facility_state': 'Kano', 'facility_type': 'public', 'facility_address': 'Zaria Road'},
    {'facility_name': 'University of Port Harcourt Teaching Hospital', 'facility_city': 'Port Harcourt', 'facility_state': 'Rivers', 'facility_type': 'public', 'facility_address': 'Choba'},
    {'facility_name': 'Braithwaite Memorial Specialist Hospital', 'facility_city': 'Port Harcourt', 'facility_state': 'Rivers', 'facility_type': 'public', 'facility_address': 'Port Harcourt'},
    {'facility_name': 'University College Hospital (UCH)', 'facility_city': 'Ibadan', 'facility_state': 'Oyo', 'facility_type': 'public', 'facility_address': 'Queen Elizabeth Road'},
    {'facility_name': 'University of Nigeria Teaching Hospital (UNTH)', 'facility_city': 'Enugu', 'facility_state': 'Enugu', 'facility_type': 'public', 'facility_address': 'Ituku-Ozalla'},
    {'facility_name': 'Ahmadu Bello University Teaching Hospital', 'facility_city': 'Zaria', 'facility_state': 'Kaduna', 'facility_type': 'public', 'facility_address': 'Zaria'},
    {'facility_name': 'Federal Medical Centre Asaba', 'facility_city': 'Asaba', 'facility_state': 'Delta', 'facility_type': 'public', 'facility_address': 'Asaba'},
    {'facility_name': 'Federal Medical Centre Owerri', 'facility_city': 'Owerri', 'facility_state': 'Imo', 'facility_type': 'public', 'facility_address': 'Owerri'},
]

print("\nSeeding sample hospitals...")
h_created = 0
for h in HOSPITALS:
    _, was_created = Facilities.objects.get_or_create(
        facility_name=h['facility_name'],
        facility_city=h['facility_city'],
        defaults={
            **h,
            'is_verified': True,
            'data_source': 'admin',
            'verified_at': timezone.now(),
        }
    )
    if was_created:
        h_created += 1
print(f"  [OK] {h_created} hospitals added ({len(HOSPITALS) - h_created} already existed)")


# ── 3. Facility Procedure Prices (the data search actually uses) ──────────────
from facilities.models import FacilityProcedure
import random

# Realistic price ranges per procedure (min, max) in Naira
# Public hospitals are cheaper, private hospitals are more expensive
PROCEDURE_PRICES = {
    # Diagnostics & Lab Tests
    'Malaria Rapid Test (RDT)':         {'public': (1000, 2000),   'private': (2500, 5000)},
    'Malaria Blood Smear':              {'public': (1500, 2500),   'private': (3000, 6000)},
    'Full Blood Count (FBC)':           {'public': (2000, 3500),   'private': (4000, 8000)},
    'Blood Group & Genotype':           {'public': (1500, 2500),   'private': (3000, 5000)},
    'HIV Test':                         {'public': (500, 1500),    'private': (2000, 5000)},
    'Hepatitis B Surface Antigen (HBsAg)': {'public': (1500, 2500), 'private': (3000, 6000)},
    'Hepatitis C Antibody Test':        {'public': (2000, 3000),   'private': (4000, 7000)},
    'Fasting Blood Sugar (FBS)':        {'public': (1000, 2000),   'private': (2500, 5000)},
    'Random Blood Sugar (RBS)':         {'public': (1000, 2000),   'private': (2000, 4000)},
    'HbA1c (Diabetes Monitoring)':      {'public': (3000, 5000),   'private': (6000, 12000)},
    'Urine Analysis (Urinalysis)':      {'public': (800, 1500),    'private': (2000, 4000)},
    'Kidney Function Test (KFT)':       {'public': (3000, 5000),   'private': (6000, 12000)},
    'Liver Function Test (LFT)':        {'public': (3000, 5000),   'private': (6000, 12000)},
    'Lipid Profile':                    {'public': (3000, 5000),   'private': (5000, 10000)},
    'Thyroid Function Test (TFT)':      {'public': (5000, 8000),   'private': (8000, 15000)},
    'Prostate Specific Antigen (PSA)':  {'public': (4000, 6000),   'private': (7000, 12000)},
    'Pregnancy Test (Urine)':           {'public': (500, 1000),    'private': (1500, 3000)},
    'Widal Test (Typhoid)':             {'public': (1500, 2500),   'private': (3000, 5000)},
    'Stool Analysis':                   {'public': (1000, 2000),   'private': (2500, 5000)},
    'Sputum AFB (TB Test)':             {'public': (1500, 3000),   'private': (3000, 6000)},
    'COVID-19 Rapid Antigen Test':      {'public': (2000, 4000),   'private': (5000, 10000)},
    'ESR (Erythrocyte Sedimentation Rate)': {'public': (1000, 2000), 'private': (2500, 5000)},
    'CRP (C-Reactive Protein)':         {'public': (2000, 3500),   'private': (4000, 8000)},
    'Electrolytes (Na, K, Cl, HCO3)':   {'public': (3000, 5000),   'private': (5000, 10000)},
    'Blood Culture & Sensitivity':      {'public': (5000, 8000),   'private': (8000, 15000)},
    'Sickle Cell Screening':            {'public': (1000, 2000),   'private': (2500, 5000)},
    # Imaging
    'Chest X-Ray':                      {'public': (3000, 5000),   'private': (8000, 15000)},
    'Abdominal X-Ray':                  {'public': (3000, 5000),   'private': (8000, 15000)},
    'Pelvic X-Ray':                     {'public': (3000, 5000),   'private': (8000, 15000)},
    'Abdominal Ultrasound':             {'public': (5000, 8000),   'private': (10000, 20000)},
    'Pelvic Ultrasound':                {'public': (5000, 8000),   'private': (10000, 20000)},
    'Obstetric Ultrasound (Antenatal Scan)': {'public': (5000, 10000), 'private': (15000, 30000)},
    'Breast Ultrasound':                {'public': (5000, 8000),   'private': (10000, 20000)},
    'Thyroid Ultrasound':               {'public': (5000, 8000),   'private': (10000, 18000)},
    'CT Scan (Head)':                   {'public': (30000, 50000), 'private': (60000, 120000)},
    'CT Scan (Chest)':                  {'public': (35000, 55000), 'private': (65000, 130000)},
    'CT Scan (Abdomen & Pelvis)':       {'public': (40000, 60000), 'private': (70000, 140000)},
    'MRI (Brain)':                      {'public': (50000, 80000), 'private': (100000, 200000)},
    'MRI (Spine)':                      {'public': (50000, 80000), 'private': (100000, 200000)},
    'Echocardiogram':                   {'public': (10000, 20000), 'private': (25000, 50000)},
    'Mammogram':                        {'public': (8000, 15000),  'private': (15000, 30000)},
    # Consultations
    'General Consultation (OPD)':       {'public': (1000, 3000),   'private': (5000, 15000)},
    'Specialist Consultation':          {'public': (3000, 5000),   'private': (10000, 30000)},
    'Paediatric Consultation':          {'public': (2000, 4000),   'private': (8000, 20000)},
    'Gynaecology Consultation':         {'public': (2000, 5000),   'private': (10000, 25000)},
    'Cardiology Consultation':          {'public': (3000, 5000),   'private': (15000, 35000)},
    'Dermatology Consultation':         {'public': (2000, 4000),   'private': (8000, 20000)},
    'ENT Consultation':                 {'public': (2000, 4000),   'private': (8000, 20000)},
    # Surgery & Procedures
    'Wound Dressing':                   {'public': (500, 1500),    'private': (2000, 5000)},
    'Suturing (Wound Closure)':         {'public': (2000, 5000),   'private': (5000, 15000)},
    'Circumcision (Paediatric)':        {'public': (5000, 10000),  'private': (15000, 35000)},
    'Circumcision (Adult)':             {'public': (10000, 20000), 'private': (25000, 50000)},
    'Hernia Repair':                    {'public': (50000, 100000),'private': (150000, 350000)},
    'Appendectomy':                     {'public': (60000, 120000),'private': (200000, 450000)},
    'Caesarean Section (C-Section)':     {'public': (80000, 150000),'private': (250000, 600000)},
    'Normal Delivery (SVD)':            {'public': (30000, 60000), 'private': (100000, 300000)},
    'ECG (Electrocardiogram)':          {'public': (2000, 4000),   'private': (5000, 10000)},
    'Blood Transfusion':                {'public': (15000, 25000), 'private': (30000, 60000)},
    'Dialysis (Haemodialysis)':         {'public': (20000, 35000), 'private': (40000, 80000)},
    # Dental
    'Dental Consultation':              {'public': (1500, 3000),   'private': (5000, 10000)},
    'Tooth Extraction (Simple)':        {'public': (3000, 5000),   'private': (8000, 15000)},
    'Tooth Extraction (Surgical)':      {'public': (10000, 20000), 'private': (25000, 50000)},
    'Dental Filling':                   {'public': (5000, 8000),   'private': (10000, 25000)},
    'Root Canal Treatment':             {'public': (15000, 30000), 'private': (40000, 80000)},
    'Scaling & Polishing':              {'public': (5000, 8000),   'private': (10000, 20000)},
    'Dental X-Ray':                     {'public': (2000, 4000),   'private': (5000, 10000)},
    # Maternity
    'Antenatal Registration':           {'public': (3000, 5000),   'private': (10000, 25000)},
    'Antenatal Visit (ANC)':            {'public': (1500, 3000),   'private': (5000, 15000)},
    'Postnatal Visit (PNC)':            {'public': (1500, 3000),   'private': (5000, 12000)},
    'Family Planning Consultation':     {'public': (500, 1500),    'private': (3000, 8000)},
    'IUD Insertion':                    {'public': (2000, 5000),   'private': (8000, 20000)},
    'Pap Smear (Cervical Cancer Screening)': {'public': (2000, 4000), 'private': (5000, 12000)},
    # Eye
    'Eye Consultation':                 {'public': (2000, 4000),   'private': (8000, 15000)},
    'Visual Acuity Test':               {'public': (1000, 2000),   'private': (3000, 6000)},
    'Glaucoma Screening':               {'public': (3000, 5000),   'private': (8000, 15000)},
    # Other
    'Physiotherapy Session':            {'public': (3000, 5000),   'private': (8000, 20000)},
    'Physiotherapy Consultation':       {'public': (2000, 4000),   'private': (5000, 12000)},
    'Emergency Consultation':           {'public': (5000, 10000),  'private': (15000, 40000)},
    'Yellow Fever Vaccination':         {'public': (2000, 4000),   'private': (5000, 10000)},
    'Tetanus Toxoid Injection':         {'public': (500, 1500),    'private': (2000, 4000)},
    'Hepatitis B Vaccination':          {'public': (2000, 4000),   'private': (5000, 10000)},
}

# Only seed prices for Lagos hospitals
LAGOS_HOSPITALS = [h for h in HOSPITALS if h['facility_state'] == 'Lagos']

# Each hospital gets a random subset of procedures with realistic prices
print("\nSeeding procedure prices for Lagos facilities...")
price_created = 0
random.seed(42)  # Reproducible prices

for hosp in LAGOS_HOSPITALS:
    try:
        facility = Facilities.objects.get(
            facility_name=hosp['facility_name'],
            facility_city=hosp['facility_city']
        )
    except Facilities.DoesNotExist:
        continue

    ftype = hosp['facility_type']  # 'public' or 'private'

    # Each facility gets 60-85% of all procedures
    procedure_names = list(PROCEDURE_PRICES.keys())
    num_to_pick = random.randint(int(len(procedure_names) * 0.6), int(len(procedure_names) * 0.85))
    selected = random.sample(procedure_names, num_to_pick)

    for proc_name in selected:
        price_range = PROCEDURE_PRICES[proc_name].get(ftype, PROCEDURE_PRICES[proc_name]['private'])
        price = random.randint(price_range[0], price_range[1])
        # Round to nearest 500
        price = round(price / 500) * 500

        source = random.choices(['provider', 'community', 'admin'], weights=[50, 30, 20])[0]

        _, was_created = FacilityProcedure.objects.get_or_create(
            facility=facility,
            procedure_name=proc_name,
            defaults={
                'price': price,
                'price_source': source,
                'community_submission_count': random.randint(0, 12) if source == 'community' else 0,
            }
        )
        if was_created:
            price_created += 1

print(f"  [OK] {price_created} procedure prices added across {len(LAGOS_HOSPITALS)} Lagos facilities")

# Also seed prices for OSM-imported Lagos facilities (if any)
osm_facilities = Facilities.objects.filter(
    is_verified=True,
    facility_state__icontains='Lagos',
    data_source='osm'
)
osm_price_created = 0
# Give OSM facilities a smaller set of common procedures
COMMON_PROCEDURES = [
    'Malaria Rapid Test (RDT)', 'Malaria Blood Smear', 'Full Blood Count (FBC)',
    'HIV Test', 'Fasting Blood Sugar (FBS)', 'Urine Analysis (Urinalysis)',
    'Pregnancy Test (Urine)', 'Widal Test (Typhoid)',
    'General Consultation (OPD)', 'Specialist Consultation',
    'Chest X-Ray', 'Abdominal Ultrasound',
    'Wound Dressing', 'ECG (Electrocardiogram)',
    'Dental Consultation', 'Tooth Extraction (Simple)',
    'Blood Group & Genotype', 'Hepatitis B Surface Antigen (HBsAg)',
    'Antenatal Registration', 'Antenatal Visit (ANC)',
    'Eye Consultation', 'Emergency Consultation',
]

for facility in osm_facilities[:50]:  # Cap at 50 OSM facilities
    ftype = facility.facility_type if facility.facility_type in ('public', 'private') else 'private'
    num_procs = random.randint(5, 15)
    selected = random.sample(COMMON_PROCEDURES, min(num_procs, len(COMMON_PROCEDURES)))

    for proc_name in selected:
        if proc_name not in PROCEDURE_PRICES:
            continue
        price_range = PROCEDURE_PRICES[proc_name].get(ftype, PROCEDURE_PRICES[proc_name]['private'])
        price = random.randint(price_range[0], price_range[1])
        price = round(price / 500) * 500

        source = random.choices(['provider', 'community', 'admin'], weights=[40, 40, 20])[0]

        _, was_created = FacilityProcedure.objects.get_or_create(
            facility=facility,
            procedure_name=proc_name,
            defaults={
                'price': price,
                'price_source': source,
                'community_submission_count': random.randint(1, 8) if source == 'community' else 0,
            }
        )
        if was_created:
            osm_price_created += 1

if osm_facilities.exists():
    print(f"  [OK] {osm_price_created} procedure prices added across {min(osm_facilities.count(), 50)} OSM facilities")

print(f"\n[DONE] Seed complete!")
print(f"   Procedures in library: {ProcedureLibrary.objects.count()}")
print(f"   Facilities: {Facilities.objects.count()}")
print(f"   Facility prices: {FacilityProcedure.objects.count()}")
