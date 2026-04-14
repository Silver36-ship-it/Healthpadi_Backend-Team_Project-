from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class UserAuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            "username": "testuser",
            "email": "test@healthpadi.com",
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": "08012345678",
            "location": "Lagos"
        }

    def test_user_registration(self):
        """Test creating a new user via the API."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "User registered successfully")
        
        # Verify user was actually created in DB
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])

    def test_user_login(self):
        """Test that a registered user can log in and receive JWT tokens."""
        # First, register the user
        User.objects.create_user(**self.user_data)
        
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify tokens are in the response
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        """Test login with wrong password."""
        User.objects.create_user(**self.user_data)
        
        login_data = {
            "email": self.user_data['email'],
            "password": "wrongpassword"
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], 'Invalid credentials')

    def test_registration_duplicate_email(self):
        """Test that registering with an existing email fails."""
        User.objects.create_user(**self.user_data)
        
        # Try to register again with same email but different username
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = "otheruser"
        
        response = self.client.post(self.register_url, duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
