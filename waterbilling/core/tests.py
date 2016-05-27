"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.test import TestCase
from .models import Config

from .management.commands import dataloader
from .utils import get_business_date
from datetime import date


class UserLoginTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(username="user1")
        user.set_password("letmein")
        user.save()

    def test_login_success(self):
        user = authenticate(username="user1", password="letmein")
        self.assertEqual(user.is_authenticated(), True)

    def test_login_failed(self):
        user = authenticate(username="user1", password="password")
        self.assertEqual(user, None)



class BusinessDateLoaderTestCase(TestCase):

    def setUp(self):
        get_business_date()

    def test_business_date_today(self):
        
        date_today_str = str(date.today())

        business_date = Config.objects.get(name='business_date').value


        self.assertEqual(date_today_str, business_date)


    def test_business_date_now(self):

        loader = dataloader.BusinessDateLoader('now')
        loader.load()


        date_today_str = str(date.today())
        business_date = Config.objects.get(name='business_date').value


        self.assertEqual(date_today_str, business_date)



    def test_business_date_value(self):
        loader = dataloader.BusinessDateLoader('2014-05-11')
        loader.load()

        business_date = Config.objects.get(name='business_date').value      

        self.assertEqual('2014-05-11', business_date)


    def test_business_date_fail(self):

        before_business_date = Config.objects.get(name='business_date').value       

        loader = dataloader.BusinessDateLoader('assdadaad')
        loader.load()

        business_date = Config.objects.get(name='business_date').value

        self.assertEqual(before_business_date, business_date)





