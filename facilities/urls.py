from django.urls import path
from facilities import views

urlpatterns = [
    # ── Public ───────────────────────────────────────────────────
    path('', views.get_facilities, name='facility-list'),
    path('nearby/', views.get_nearby_facilities, name='facility-nearby'),
    path('<int:pk>/', views.get_facility_detail, name='facility-detail'),
    path('<int:pk>/pricing/', views.facility_pricing, name='facility-pricing'),
    path('<int:pk>/pricing/<int:price_id>/', views.facility_pricing_detail, name='facility-pricing-detail'),
    path('<int:pk>/price-history/', views.facility_price_history, name='facility-price-history'),
    path('<int:pk>/community-prices/', views.facility_community_prices, name='facility-community-prices'),

    # ── Provider ──────────────────────────────────────────────────
    path('mine/', views.my_facilities, name='my-facilities'),
    path('create/', views.create_facility, name='facility-create'),
    path('<int:pk>/update/', views.update_facility, name='facility-update'),
    path('<int:pk>/delete/', views.delete_facility, name='facility-delete'),
    path('<int:pk>/claim/', views.claim_facility, name='facility-claim'),
    path('my-claims/', views.my_claims, name='my-claims'),

    # ── Community ─────────────────────────────────────────────────
    path('community-prices/', views.submit_community_price, name='community-price-submit'),

    # ── Admin ─────────────────────────────────────────────────────
    path('admin/pending/', views.pending_facilities, name='facility-pending'),
    path('admin/create/', views.admin_create_facility, name='admin-facility-create'),
    path('admin/import/', views.bulk_import_facilities, name='facility-bulk-import'),
    path('admin/sync-osm/', views.sync_from_osm, name='facility-sync-osm'),
    path('admin/claims/', views.pending_claims, name='facility-claims-pending'),
    path('<int:pk>/approve/', views.approve_facility, name='facility-approve'),
    path('<int:pk>/reject/', views.reject_facility, name='facility-reject'),
    path('claims/<int:pk>/approve/', views.approve_claim, name='claim-approve'),
    path('claims/<int:pk>/reject/', views.reject_claim, name='claim-reject'),

    # ── Procedure Library ─────────────────────────────────────────
    path('procedures/library/', views.procedure_library, name='procedure-library'),
    path('procedures/library/add/', views.add_procedure_to_library, name='procedure-library-add'),
]
