from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from providers.models import Providers
from facilities.models import Facilities

class SearchTests(APITestCase):
    def setUp(self):
        self.search_url = reverse('global-search')
        
        # Create a test provider
        self.provider = Providers.objects.create(
            provider_name="General Hospital",
            provider_city="Lagos",
            provider_type="Public",
            is_verified=True
        )
        
        # Create a test facility linked to the provider
        self.facility = Facilities.objects.create(
            provider=self.provider,
            facility_name="Lagos Central Clinic",
            facility_city="Lagos",
            facility_state="Lagos State",
            facility_address="Ikeja",
            is_verified=True
        )

    def test_search_by_name(self):
        """Test searching for a facility by name."""
        response = self.client.get(f"{self.search_url}?q=Lagos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if the facility appears in the search results
        self.assertTrue(any(f['facility_name'] == "Lagos Central Clinic" for f in response.data['facilities']))
        # Check if the provider also appears since it has 'Lagos' in its city
        self.assertTrue(any(p['provider_name'] == "General Hospital" for p in response.data['providers']))

    def test_search_no_query(self):
        """Test search with no query returns empty lists."""
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['providers']), 0)
        self.assertEqual(len(response.data['facilities']), 0)

    def test_search_no_results(self):
        """Test search with a term that doesn't exist."""
        response = self.client.get(f"{self.search_url}?q=NonExistentPlace")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['providers']), 0)
        self.assertEqual(len(response.data['facilities']), 0)
