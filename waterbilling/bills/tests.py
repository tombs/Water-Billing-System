"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from csv import DictReader
from os.path import dirname, join, normpath
from django.test import TestCase
from django.conf import settings
from .models import Account, Bill
from core.management.commands.dataloader import RateLoader, AccountTypeLoader, RateChargeLoader, BillingScheduleLoader, FelizanaLoader
from decimal import Decimal

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class SimpleBillingComputation(TestCase):
    '''

    Class tests for billing computation, using 

    '''
    def setUp(self):

        settings.DEBUG = True
        RateLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/rate.csv'))).load()
        AccountTypeLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/accounttype.csv'))).load()
        RateChargeLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/ratecharge.csv'))).load()
        BillingScheduleLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/billingschedule.csv'))).load()
        FelizanaLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/felizana_customer_info_2014-02.csv'))).load()
        
    def test_usage_zero(self):
        '''

        Details: Usage = 0, account = 483 bill date = 2014-02-10

        Expected Result:  Amount due = 156.00

        '''

        account = Account.objects.get(pk=483)

        self.assertEqual(account.status,u'active')

        bill, created = account.generate_bill(business_date='2014-02-10', period=13)

        self.assertEqual(bill.amount_due, Decimal('156.00'))


    def test_usage_ten(self):
        '''

        Details: Usage = 0, account = 483 bill date = 2014-02-10

        Expected Result:  Amount due = 156.00

        '''

        account = Account.objects.get(pk=483)

        self.assertEqual(account.status,u'active')

        bill, created = account.generate_bill(business_date='2014-02-10', period=13)

        self.assertEqual(bill.amount_due, Decimal('156.00'))



    def test_usage_between_5_and_10(self):
        '''

        Details: Usage = 5, account = 274 bill date = 2014-02-10

        Expected Result:  Amount due = 156.00

        '''

        account = Account.objects.get(pk=274)

        self.assertEqual(account.status,u'active')

        bill, created = account.generate_bill(business_date='2014-02-10', period=13 )

        self.assertEqual(bill.amount_due, Decimal('156.00'))



    def test_usage_between_10_and_20(self):
        '''

        Details: Usage = 16, account = 14 bill date = 2014-02-10

        Expected Result:  Amount due = 254.40

        '''

        account = Account.objects.get(pk=14)

        self.assertEqual(account.status,u'active')

        bill, created = account.generate_bill(business_date='2014-02-10', period=13)
        
        self.assertEqual(bill.amount_due, Decimal('254.40'))


    def test_usage_between_20_and_30(self):

        '''

        Details: Usage = 27, account = 127 bill date = 2014-02-10

        Expected Result:  Amount due = 440.40

        '''

        account = Account.objects.get(pk=127)

        self.assertEqual(account.status,u'active')

        bill, created = account.generate_bill(business_date='2014-02-10', period=13)
        
        self.assertEqual(bill.amount_due, Decimal('440.40'))




    def test_usage_between_30_and_40(self):

        '''

        Details: Usage = 34, account = 103 bill date = 2014-02-10

        Expected Result:  Amount due = 567.20

        '''

        account = Account.objects.get(pk=103)

        self.assertEqual(account.status,u'active')

        bill, created = account.generate_bill(business_date='2014-02-10', period=13)
        
        self.assertEqual(bill.amount_due, Decimal('567.20'))
