from django.test import TestCase
from rest_framework.test import APIClient

from facilities.models import Facilities, FacilityProcedure


class FacilityListTests(TestCase):
    def setUp(self):
        self.lagos_facility = Facilities.objects.create(
            facility_name='Lagos Medical Centre',
            facility_city='Lagos',
            facility_state='Lagos',
            facility_type='private',
            is_verified=True,
        )
        self.kano_facility = Facilities.objects.create(
            facility_name='Kano General Hospital',
            facility_city='Kano',
            facility_state='Kano',
            facility_type='public',
            is_verified=False,
        )
        FacilityProcedure.objects.create(
            facility=self.kano_facility,
            procedure_name='Malaria Rapid Test',
            price='1500.00',
        )
        self.client = APIClient()

    def test_list_returns_all_facilities_and_their_procedures(self):
        response = self.client.get('/api/facilities/')

        self.assertEqual(response.status_code, 200)
        facilities_by_id = {
            facility['facility_id']: facility
            for facility in response.data
        }
        self.assertEqual(
            set(facilities_by_id),
            {self.lagos_facility.facility_id, self.kano_facility.facility_id},
        )
        self.assertEqual(
            facilities_by_id[self.kano_facility.facility_id]['pricing'][0]['procedure_name'],
            'Malaria Rapid Test',
        )

    def test_list_preserves_optional_state_filter(self):
        response = self.client.get('/api/facilities/', {'state': 'Kano'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [facility['facility_id'] for facility in response.data],
            [self.kano_facility.facility_id],
        )

    def test_list_uses_prefetched_pricing_without_per_facility_queries(self):
        with self.assertNumQueries(3):
            response = self.client.get('/api/facilities/')

        self.assertEqual(response.status_code, 200)
