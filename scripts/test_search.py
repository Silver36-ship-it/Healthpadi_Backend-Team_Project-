import requests

BASE = 'http://localhost:8000/api'

tests = [
    ("Malaria Test", None),
    ("Malaria Test Ikeja", "should filter to Ikeja"),
    ("Malaria Ikeja", "exact match in Ikeja"),
    ("X-Ray Victoria Island", "filter to VI"),
    ("Antenatal Surulere", "filter to Surulere"),
    ("Chest X-Ray", "standard search"),
    ("MRI Lekki", "filter to Lekki"),
    ("Consultation", "broad search"),
]

for query, note in tests:
    r = requests.get(f'{BASE}/search/?q={query}')
    data = r.json()
    count = len(data['results'])
    # Show unique facilities
    facilities = set()
    for x in data['results']:
        facilities.add(f"{x['facility_name']} ({x['facility_address']})")
    
    print(f"'{query}' -> {count} results" + (f"  [{note}]" if note else ""))
    for f in sorted(facilities):
        print(f"    {f}")
    print()

print("ALL DONE")
