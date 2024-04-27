from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Ride, CustomUser
from api.serializers import RideSerializer
from django.contrib.auth import get_user_model


class RideModelTest(TestCase):

    def test_create_ride(self):
        user = CustomUser.objects.create(username='test_user', password='test_password')
        ride = Ride.objects.create(rider=user, pickup_location='Start Point', dropoff_location='End Point')
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

class RideViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='test_user', password='test_password')
        self.client.force_authenticate(user=self.user) 

    def test_create_ride_success(self):
        data = {'pickup_location': 'Start Point', 'dropoff_location': 'End Point'}
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
        ride = Ride.objects.create(rider=self.user, pickup_location='Start', dropoff_location='End')
        data = {'status': 'INVALID_STATUS'}  
        response = self.client.put(f'/api/Rides/{ride.pk}/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_driver_accept_ride_success(self):
        driver = get_user_model().objects.create_user(username='driver_user', password='driver_password')
        ride = Ride.objects.create(rider=self.user, driver=driver, pickup_location='Start', dropoff_location='End')
        self.client.force_authenticate(user=driver) 

        response = self.client.post(f'/api/Driver/{ride.pk}', format='json') 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Ride.objects.get(pk=ride.pk).driver_accepted, True)

    def test_driver_accept_ride_unauthorized(self):
        driver = get_user_model().objects.create_user(username='driver_user', password='driver_password')
        ride = Ride.objects.create(rider=self.user, driver=driver, pickup_location='Start', dropoff_location='End')

        response = self.client.post(f'/api/Driver/{ride.pk}', format='json') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)