from django.test import TestCase

# Create your tests here.

import requests
import unittest
from django.test import Client
from django.urls import reverse
from .models import User_Profiles
from django.contrib.auth.models import User
from .forms import SignUpForm

class SignUpTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('new')
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'user_type': '0',
        }

    def test_create_student(self):
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Success! New user created.')
        user = User.objects.get(username='testuser')
        self.assertEqual(user.profile.user_type, '0')
        print('Student profile successfully created via server')

    def test_create_instructor(self):
        self.user_data['user_type'] = '1'
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Success! New user created.')
        user = User.objects.get(username='testuser')
        self.assertEqual(user.profile.user_type, '1')
        print('Instructor profile successfully created via server')

    def tearDown(self):
        user = User.objects.get(username='testuser')
        user.delete()
