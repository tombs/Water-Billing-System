"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User


class LoginTest(TestCase):

    def create_test_super_user(self):
        user = User(username='test_user', email='test_user@example.com')
        user.set_password = 'password'

        user.save()


    def setUp(self):
        self.create_test_super_user()
        self.client = Client()


    def test_login_pass(self):

        response = self.client.post('/login', {'username':'test_user', 'password':'password'})

        self.assertNotContains(response,'Invalid username/password combination, please try again', status_code=301)


    def test_login_failed(self):
        response = self.client.post('/login/?next=/', {'username':'test_user', 'password':'password1'})
        
        self.assertContains(response,'Invalid username/password combination, please try again',status_code=200)        

