from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Ride, CustomUser
from api.serializers import RideSerializer
from django.contrib.auth import get_user_model
from api.views import close_driver

# To check comma-separated latitude, longitude format-current location
def is_valid_location(location):
    try:
        lat, lng = location.split(",")
        float(lat)
        float(lng)
        return True
    except ValueError:
        return False
# Ride Model Test
class RideModelTest(TestCase):

    def test_create_ride(self):
        user = CustomUser.objects.create(username='test_user', password='test_password')
        ride = Ride.objects.create(rider=user, pickup_location='Start Point', dropoff_location='End Point', current_location='10.850517,76.271080')
        self.assertEqual(ride.status, 'REQUESTED')
        self.assertEqual(ride.driver_accepted, False)

    def test_ride_relationships(self):
        user = CustomUser.objects.create(username='test_user', password='test_password')
        ride = Ride.objects.create(rider=user, pickup_location='Start Point', dropoff_location='End Point')
        self.assertEqual(ride.rider, user)

    def test_ride_str_method(self):
        user = CustomUser.objects.create(username='test_user', password='test_password', name='Test Name')
        ride = Ride.objects.create(rider=user, pickup_location='Start Point', dropoff_location='End Point')
        self.assertEqual(str(ride), 'Test Name')

    def test_create_ride_valid_current_location(self):
        user = CustomUser.objects.create(username='test_user', password='test_password', current_location='10.0,20.0')
        ride = Ride.objects.create(rider=user, pickup_location='Start Point', dropoff_location='End Point', current_location='10.0,20.0')
        self.assertEqual(ride.status, 'REQUESTED')
        self.assertEqual(ride.driver_accepted, False)
        self.assertTrue(is_valid_location(ride.current_location))


# Login API Test
class LoginApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='test_user', password='test_password')

    def test_login_success(self):
        data = {'username': 'test_user', 'password': 'test_password'}
        response = self.client.post('/api/Login', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_details', response.data)

    def test_login_invalid_credentials(self):
        data = {'username': 'test_user', 'password': 'wrong_password'}
        response = self.client.post('/api/Login', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('message', response.data)

# Registration API Test
class RegistrationApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_registration_success(self):
        data = {'username': 'new_user', 'password': 'new_password', 'phone_number': '1234567890'}
        response = self.client.post('/api/Registration', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_details', response.data)

    def test_registration_existing_username(self):
        data = {'username': 'test_user', 'password': 'new_password', 'phone_number': '1234567890'}
        get_user_model().objects.create_user(username='test_user', password='test_password')
        response = self.client.post('/api/Registration', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_missing_fields(self):
        data = {'password': 'new_password'}
        response = self.client.post('/api/Registration', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

# # Ride View Test
class RideViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='test_user', password='test_password')
        self.client.force_authenticate(user=self.user)

    def test_create_ride_success(self):
        data = {'pickup_location': 'Start Point', 'dropoff_location': 'End Point', 'current_location': '10.850517,76.271080'}
        response = self.client.post('/api/Rides/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ride.objects.count(), 1)
        self.assertEqual(Ride.objects.first().rider, self.user)

    def test_create_ride_missing_fields(self):
        data = {}
        response = self.client.post('/api/Rides/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pickup_location', response.data)
        self.assertIn('dropoff_location', response.data)

    def test_update_ride_status_success(self):
        ride = Ride.objects.create(rider=self.user, pickup_location='Start', dropoff_location='End')
        data = {'status': 'STARTED'}
        response = self.client.put(f'/api/Rides/{ride.pk}/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Ride.objects.get(pk=ride.pk).status, 'STARTED')

    def test_update_ride_status_invalid_status(self):
        ride = Ride.objects.create(rider=self.user, pickup_location='10.0,20.0', dropoff_location='30.0,40.0')
        data = {'status': 'INVALID_STATUS'}
        response = self.client.put(f'/api/Rides/{ride.pk}/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_driver_accept_ride_success(self):
        driver = get_user_model().objects.create_user(username='driver_user', password='driver_password', role='2')
        ride = Ride.objects.create(rider=self.user, driver=driver, pickup_location='Start', dropoff_location='End')
        self.client.force_authenticate(user=driver)
        response = self.client.post(f'/api/Driver/{ride.pk}', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Ride.objects.get(pk=ride.pk).driver_accepted, True)

    def test_driver_accept_ride_unauthorized(self):
        driver = get_user_model().objects.create_user(username='driver_user', password='driver_password', role='2')
        ride = Ride.objects.create(rider=self.user, driver=driver, pickup_location='Start', dropoff_location='End')
        response = self.client.post(f'/api/Driver/{ride.pk}', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_close_driver_no_current_location(self):
        rider = Ride.objects.create(pickup_location='10.0,20.0')
        driver = CustomUser.objects.create(role='2')

        closest_driver = close_driver(rider)
        self.assertIsNone(closest_driver)

    def test_close_driver_empty_available_drivers(self):
        rider = Ride.objects.create(pickup_location='10.0,20.0')
        closest_driver = close_driver(rider)
        self.assertIsNone(closest_driver)

        
