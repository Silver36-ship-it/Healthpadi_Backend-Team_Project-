# HealthPadi Backend — Setup & Migration Guide

## What changed in this update

### New models (require migrations)
- `Facilities` — 6 new fields: `osm_id`, `phone`, `opening_hours`, `osm_synced_at`, `data_source`, `is_claimed`, `claimed_by`
- `FacilityProcedure` — 2 new fields: `price_source`, `community_submission_count`
- `PriceHistory` (NEW) — auto-tracks every price change
- `CommunityPriceSubmission` (NEW) — crowdsourced prices from patients
- `FacilityClaim` (NEW) — providers claiming facilities

### Fixed bugs
- `facilities/views.py` — every function was defined twice. Now clean with no duplicates.
- `notification/views.py` — `from_email=''` fixed to use `settings.DEFAULT_FROM_EMAIL`
- `user/urls.py` — added missing `/api/users/token/refresh/` endpoint
- `healthpadi/settings.py` — SECRET_KEY now from .env, pagination added, Africa/Lagos timezone

### New features
- OSM sync: `POST /api/facilities/admin/sync-osm/` — pulls hospitals from OpenStreetMap for free
- Facility claims: providers claim existing facilities instead of creating from scratch
- Price history: auto-saved on every price change via Django signal
- Community prices: patients submit what they were charged
- No dead ends in search: zero results now returns fallback facilities with phone numbers
- Meaningful verified badge: `is_truly_verified` = admin approved + prices updated within 30 days
- Stale price warning: `is_price_stale` = true if no price updated in 30+ days

---

## Steps to run after replacing files

### 1. Set up your .env file
```bash
cp .env.example .env
# Edit .env with your MySQL password and a proper SECRET_KEY
```

### 2. Create migrations for all model changes
```bash
uv run manage.py makemigrations facilities
uv run manage.py makemigrations
```

### 3. Apply migrations
```bash
uv run manage.py migrate
```

### 4. Seed the database
```bash
uv run python scripts/seed_data.py
```

### 5. Create a superuser (admin)
```bash
uv run manage.py createsuperuser
```

### 6. Run the server
```bash
uv run manage.py runserver
```

---

## Key API endpoints added

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | /api/facilities/mine/ | Provider | My claimed facilities only |
| POST | /api/facilities/{id}/claim/ | Provider | Claim a facility |
| GET | /api/facilities/my-claims/ | Provider | My claim statuses |
| GET | /api/facilities/admin/claims/ | Admin | All pending claims |
| PATCH | /api/facilities/claims/{id}/approve/ | Admin | Approve claim |
| PATCH | /api/facilities/claims/{id}/reject/ | Admin | Reject claim |
| POST | /api/facilities/admin/sync-osm/ | Admin | Sync from OpenStreetMap |
| GET | /api/facilities/{id}/price-history/ | Public | Price change history |
| GET | /api/facilities/{id}/community-prices/ | Public | Community submissions |
| POST | /api/facilities/community-prices/ | Auth | Submit community price |
| GET | /api/users/token/refresh/ | Public | Refresh JWT token |

---

## OSM Sync — How to populate facilities for free

In the admin dashboard, trigger a sync for any Nigerian city:

```json
POST /api/facilities/admin/sync-osm/
{
  "city": "Lagos",
  "state": "Lagos",
  "radius_km": 50
}
```

This calls OpenStreetMap's Overpass API (completely free, no key needed) and saves
all hospitals, clinics, and pharmacies found within 50km of Lagos.

Run for major cities to get started:
- Lagos, Port Harcourt, Abuja, Kano, Ibadan, Enugu, Kaduna, Benin City
