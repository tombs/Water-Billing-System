# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.db import transaction

from django.utils.timezone import now
from django.db.models import Sum, Max, F
from audit_log.models.managers import AuditLog


class CoreModel(models.Model):

    created = models.DateTimeField(default=now, editable=False)
    created_by = models.TextField(db_column='created_by', blank=False, editable=False)
    last_updated = models.DateTimeField(default=now, db_column='last_updated', editable=False)
    last_updated_by = models.TextField(db_column='last_updated_by', blank=False, editable=False)

    class Meta:
        abstract = True


class Config(CoreModel):

    class Meta:
        db_table = 'config'
        verbose_name = "configuration"
        verbose_name_plural = "configurations"
    
    name = models.TextField(blank=False)
    value = models.TextField(blank=False)

    audit_log = AuditLog()




class AccountException(Exception):
    pass

class Account(CoreModel):
    """
    Account is defined by a customer and address.
    Customers can have multiple accounts with different addresses.
    An Account is mapped to a Meter.
    Should the Meter be destroyed, close the account and create a new one with a new meter, but same customer and address
    """
    customer = models.ForeignKey('Customer', db_column='customer_id')
    address = models.ForeignKey('Address', db_column='address_id')
    account_type = models.ForeignKey('AccountType', db_column='account_type_id')
    #meter = models.ForeignKey('Meter', db_column='meter_id', unique=True)
    status = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'account'
        ordering = ['customer']
        unique_together = ('customer', 'address')

    def __unicode__(self):
        return u'-'.join([unicode(self.customer),unicode(self.address)])

    @property
    def bills(self):
        return self.bill_set.all()

    @property
    def notices(self):
        return self.notice_set.all()

    @property
    def meterreads(self):
        return self.meterread_set.all()

    @property
    def adjustments(self):
        return self.adjustment_set.all()

    @property
    def meters(self):
        meters = [meter  for meter in  self.accountmeter_set.all()]
        return meters

    @property
    def accountmeters(self):
        return  self.accountmeter_set.all()

    @property
    def notes(self):
        return  self.accountnote_set.all()

    @property
    def balance(self):
        return self.financialtransaction_set.latest('id').balance

    @property
    def latest_balance(self):
        return self.financialtransaction_set.latest('id').balance
    # @property
    # def latest_balance_(self):
    #     posted_payment = self.payment_set.filter(status="posted",
    #                     payment_date__gte=self.latest_bill.bill_date).aggregate(Sum('amount'))['amount__sum']
    #     if not posted_payment:
    #         posted_payment = Decimal('0.0')
    #     if self.latest_bill:
    #         return self.latest_bill.amount_due - posted_payment

    #     return None

    @property
    def is_for_disconnection(self):
        ''' 

        Returns true if the account is for disconnection

        '''
        if self.status == 'for disconnection':
            return True

        return False

    def for_disconnection(self):
        self.status = 'for disconnection'
        self.update()

    def is_disconnected(self):
        ''' 

        Returns true if the account is for disconnection

        '''
        if self.status == 'disconnected':
            return True

        return False


    def disconnect(self):
        ''' Set status of account to disconnected'''
        self.status = 'disconnected'
        self.update()



    @property
    def bill(self):
        ''' 

        Returns the bill of the current active period, None of none.

        '''
        period = Config.objects.get(name='active_period').value

        bs = BillingSchedule.objects.get(pk=period)


        bill = Bill.objects.filter(account=self, billing_schedule=bs)  
       
        if self.has_bill():
            return bill.get()

        return None


    def has_bill(self, period=None):
        '''

        Determines if the account has a bill for a particular period (default is active period)

        '''
        has_bill = False

        if period is None:
            period = Config.objects.get(name='active_period').value
        
        bs = BillingSchedule.objects.get(pk=period)

        bill = Bill.objects.filter(account=self, billing_schedule=bs)

        if bill.count() > 0 :
            has_bill = True

        return has_bill

    @property
    def latest_bill(self):
        if self.bill_set.exists():
            return self.bill_set.latest('id')
        return None

    @property
    def latest_notice(self):
        if self.notice_set.exists():
            return self.notice_set.latest('id')
        return None

    @property
    def reconnection_fees(self):
        if self.latest_bill:
            return self.financialtransaction_set.filter(type='reconnection_fee', 
                        transaction_date__gte=self.latest_bill.bill_date).aggregate(Sum('amount'))['amount__sum']
        return None

    @property
    def total_posted_payment(self):
        if self.latest_bill:
            return self.financialtransaction_set.filter(type='posted_payment', 
                        transaction_date__gte=self.latest_bill.bill_date).aggregate(Sum('amount'))['amount__sum']
        return None

    @property
    def total_adjustment(self):
        if self.latest_bill:
            credit = self.financialtransaction_set.filter(adjustment__type='credit', transaction_date__gte=self.latest_bill.bill_date).aggregate(Sum('amount'))['amount__sum']
            debit = self.financialtransaction_set.filter(adjustment__type='debit', transaction_date__gte=self.latest_bill.bill_date).aggregate(Sum('amount'))['amount__sum']
            reconnection_fee = self.financialtransaction_set.filter(adjustment__type='reconnection_fee', transaction_date__gte=self.latest_bill.bill_date).aggregate(Sum('amount'))['amount__sum']
            
            #if credit is None and debit is None:
            if credit is None and debit is None and reconnection_fee is None:
                return Decimal('0.00')

            #return credit - debit
            return credit - debit - reconnection_fee

        return Decimal('0.00')

    def regenerate_bill(self,user=''):
        """

        This function executes delete_current_bill and generate_bill in succession.
        This regenerates an accounts current bill (or creates a new one if no bill is currently existing)
        for the given active period.

        """
        deleted = self.delete_current_bill(user=user)
        created = False
        if deleted:
            print "-- original bill deleted"
            bill, created = self.generate_bill()
        else:
            print "-- no bill to delete. generating anyway.."
            bill, created = self.generate_bill()

        return bill, created

    def delete_current_bill(self, business_date=None, period=None, user=''):    
        """
        delete the bill for the current period. This feature is used for corrections in bill generation.
        The related FinancialTransaction must also be deleted (currently unable to delete due to foreign key constraint).
        """
        deleted = False

        if period is None:
            period = Config.objects.get(name='active_period').value
 
            business_date = Config.objects.get(name='business_date').value


        billing_schedule = BillingSchedule.objects.get(pk=period)

        bill = self.bill
        if bill:
            try:
   
                penalties = billing_schedule.penalty_set.filter(
                    account_id=self.id,
                    type='overdue')
                penalty_amount = penalties.aggregate(Sum('amount'))['amount__sum']
                print "penalty amount: ", penalty_amount
                if penalty_amount is None:
                    penalty_amount = Decimal('0.0')
                penalties.delete()

                if self.balance > 0:
                    ft_balance = self.balance - penalty_amount
                else:
                    ft_balance = self.balance

                bill.meter_read.readcharge_set.all().delete()
                #ft = bill.financial_transaction
                #ft.delete() 

                self.financial_transaction = FinancialTransaction.objects.create(
                    account_id=self.id,
                    amount = bill.amount_due,
                    balance = ft_balance - bill.current_charge,
                    type = 'bill_deletion',
                    transaction_date = business_date)
                bill.create_deleted_copy(deletor=user)
                bill.delete()
                deleted = True
            except Exception, e:
                print "-- an error occurred.. exiting: %s"%e
                return deleted

        else:
            print "-- no bill to delete for this period!"

        return deleted





    def generate_bill(self, business_date=None, period=None):
        """
        generate bills for this billing schedule
        return a list of tuple of instance and True/False if created
        """
        # get active period from Config
        if period is None:
            period = Config.objects.get(name='active_period').value
 
            business_date = Config.objects.get(name='business_date').value
        
        #meter read must be within billing schedule
        if self.status=='inactive':
            return None, False
        
        previous_balance = self.latest_balance
        
        #billing_schedule = BillingSchedule.objects.get(start_date__lte = business_date, end_date__gte = business_date)
        billing_schedule = BillingSchedule.objects.get(pk=period)
        
        #mr = self.meter.meterread_set.filter(read_date__lte=business_date).latest('id')
        #mr = self.meter.meterread_set.filter(billing_schedule=billing_schedule, account=self).latest('id')
        usage, mr = self.get_meter_reads_usage(period=period)
        
        print "mr: ", type(mr), mr

        if mr is None:
            print "No reads for this period"
            return None, False
        
        #if billing_schedule.start_date>mr.read_date or billing_schedule.end_date < mr.read_date:
        #     return None, False            
        bill, created = Bill.objects.get_or_create(account = self, billing_schedule=billing_schedule, meter_read = mr,bill_date = business_date)
        
        if created:
            mr.status='used'
            mr.update()
            
            print "account balance: ", self.latest_balance
            #if previous_balance > Decimal("0.0"):
            #    print " account: %s  for disconnection " % (self.customer.last_name + ", " + self.customer.first_name)
            #    self.status = "for disconnection"
            #    self.save()
            
        
        return bill, created

    def generate_notice(self, business_date=None, period=None):
        """
        generate notices for this billing schedule
        1. Check if there is already a notice for the billing schedule
        2. Check if there is a bill already created, get it and base the due date
        FIXME: lots of hardcoded numbers
        """
        from datetime import timedelta
        
        # get active period from Config
        if period is None:
            period = Config.objects.get(name='active_period').value

        if business_date is None:
            business_date = Config.objects.get(name='business_date').value

        if self.status=='inactive':
            return None, False

        notice_date = business_date
        reconnection_fee = Decimal('200.0')
        #billing_schedule = BillingSchedule.objects.get(start_date__lte=business_date, end_date__gte=business_date)
        billing_schedule = BillingSchedule.objects.get(pk=period)
        notice = self.latest_notice
        if notice and notice.billing_schedule == billing_schedule:
            return notice, False

        elif self.latest_bill and self.latest_balance > Decimal("0.0") and self.latest_bill.billing_schedule == billing_schedule:

            amount = self.latest_balance
            due_date = self.latest_bill.due_date + timedelta(days=7) #FIX-ME: The notice period shoud be in Config

            self.for_disconnection()

            return  Notice.objects.get_or_create(account = self, 
                        billing_schedule=billing_schedule, notice_date = notice_date, 
                        due_date = due_date, reconnection_fee = reconnection_fee, 
                        amount=amount)
        else:
            print 'no notice generated'
            return None, False

    @property
    def meter(self):
        meter = self.get_meter()

        return meter

    def get_meter(self):
        '''

        Get the meter from the active account meter

        '''
        meter = self.get_account_meter().meter
        #self.meter = meter
        return meter

    def get_account_meter(self):
        '''

        Get the active account meter for the Account from the AccountMeter table.
        Return None if no AccountMeter exists for the acount.

        '''
        account_meter = AccountMeter.objects.filter(account = self, status='active')
        if account_meter.count() > 0:
            return account_meter.get()

        return None

    
    def add_account_meter(self, new_meter):
        '''

        Assign a new meter to the account.  This adds the meter to the AccountMeter table, and sets the meter as 'active'

        '''
        print "--- Entering add account meter "
        new_meter = Meter.objects.get(pk=new_meter)
        current_meter = None
        current_account_meter = self.get_account_meter()

        #deactivate current account meter if existing

        print "current_account_meter: ",current_account_meter
        print "--- Deactivate current account meter "
        if current_account_meter is not None:
            print "meter: ", current_account_meter.meter
            current_meter = current_account_meter.meter
            current_account_meter.status = 'inactive'
            current_account_meter.save()

        print "--- Create a new account meter"
        print "--- self: ", self

        #below is encountering a UnicodeDecode Error. Manually doing for the meantime.
        new_account_meter, created = AccountMeter.objects.get_or_create(account = self, meter=new_meter)

        #new_account_meter =AccountMeter.objects.filter(account=self, meter=new_meter)        
#
        #print "new_account_meter: ", new_account_meter
        #print "type: ", type(new_account_meter)
        #if new_account_meter.count() > 0:
        #    new_account_meter = new_account_meter.get()
        #else:
        #    new_account_meter = AccountMeter(account=self, meter=new_meter)
        
        print "account meter: " + str(new_account_meter.meter.meter_uid)
        new_account_meter.status = 'active'      
        new_account_meter.save()
        #self.meter = new_meter  

        return new_account_meter




    def add_meter_read(self, current_reading, read_date=None, period=None):
        '''

        Add a meter read for the specified account, read date, and billing period (Billing Schedule)

        '''
        from datetime import time

        if period is None:
            period = Config.objects.get(name='active_period').value

        if read_date is None:
            read_date = Config.objects.get(name='business_date').value

        bs = BillingSchedule.objects.get(pk=period)
        meter = self.get_meter()

        print "self.get_current_reading: ", self.get_current_reading()
        previous_reading = self.get_current_reading()
        print "--- previous_reading: ", previous_reading
        print "--- decimal previous reading: ", Decimal(previous_reading)
        usage = Decimal(current_reading) - Decimal(previous_reading)

        meterread, created = MeterRead.objects.get_or_create(meter = meter, account = self , billing_schedule = bs,
                                read_date=read_date,
                                defaults={
                                            'read_time':time(),
                                            'current_reading':current_reading,
                                            'previous_reading': previous_reading,
                                            'usage':usage
                                        })
        if created:
            print "--- New Meter Read: ", meterread.id
            #This is a new read, save all the values
            meterread.previous_reading = previous_reading
            meterread.usage = usage
            meterread.current_reading = current_reading
            meterread.read_time = time()
        else:
            print "-- Old Meter Read: ", meterread.id 
            print "-- Updating with current_reading: ", current_reading
            # This is an old read, simply update the current reading, and get the new usage
            meterread.current_reading = current_reading
            meterread.read_time = time()
            meterread.usage = Decimal(meterread.current_reading) - Decimal(meterread.previous_reading) 

        meterread.update()

        print "meterread", meterread, created
        print "meterread.id: ", meterread.id
        print "meterread.previous_reading: ", meterread.previous_reading
        print "meterread.current_reading: ", meterread.current_reading
        print "meterread.usage: ", meterread.usage
        print "- - - - - - "

    @property
    def usage(self):
        usage, meter = self.get_meter_reads_usage()

        return usage

    def get_meter_read_usage(self, meter=None, period=None):
        '''

        Get the usage the latest read of an account meter for a particular period.
        By the default it gets the usage of an active meter.

        '''
        # get the active meter
        if meter is None:
            meter = self.get_meter()
        else: 
            meter = Meter.objects.get(pk=meter)

        # get the active period
        if period is None:
            period = Config.objects.get(name='active_period').value

        bs = BillingSchedule.objects.get(pk=period)
        reads = MeterRead.objects.filter(billing_schedule=bs,account=self, meter=meter)

        usage = Decimal("0.00")
        if reads.count() > 1:
            for read in reads:
                usage = usage + read.usage
            return usage
        elif reads.count() == 1:
            return reads.get().usage
        else:
            return usage

    def get_meter_reads_usage(self, period=None):
        '''

        Retrieve all meter reads for an Account for a specific period (BillingSchedule).
        Return latest MeterRead

        '''
        if period is None:
            period = Config.objects.get(name='active_period').value


        bs = BillingSchedule.objects.get(pk=period)
        reads = MeterRead.objects.filter(billing_schedule=bs,account=self)

        usage = Decimal("0.0")

        for read in reads:
            usage = usage + Decimal(read.usage)

        reads_id = None
        if reads.count() > 0:
            reads_id = reads.latest('id')
        
        return usage, reads_id


    def add_payment(self, amount, payment_type='cash', check_number='', payment_date=None, remarks=''):
        '''

        Adds a payment to an account

        '''
        print "adding payment to account id: ", self.id
        if payment_date is None:
            payment_date = Config.objects.get(name='business_date').value

        auto_post = Config.objects.get(name='auto_post').value

        print "amount: ", Decimal(amount)
        print "check_number: ", check_number
        print "type: ", payment_type
        print "remarks: ", remarks

        payment = Payment(account=self, amount=Decimal(amount), payment_date=payment_date, check_number=check_number,
            type=payment_type, remarks=remarks)

        payment.save()

        print "payment_date: ", payment_date
        print "payment_id: ", payment.id

        if auto_post =='True' and payment_type == 'cash':
            "auto posting payment.."
            pp = PostedPayment(payment=payment)
            pp.save()

        return payment


    def add_adjustment(self, amount, adjustment_type='credit',  adjustment_date=None, description=''):
        '''

        Adds an adjustment to an account

        '''
        print "adding adjustment to account id: ", self.id
        if adjustment_date is None:
            adjustment_date = Config.objects.get(name='business_date').value

        auto_post = Config.objects.get(name='auto_post').value

        print "amount: ", Decimal(amount)
        print "type: ", adjustment_type
        print "description: ", description
    
        adjustment = Adjustment(account=self, amount=Decimal(amount), adjustment_date=adjustment_date,  
            type=adjustment_type, description=description)

        adjustment.save()

        print "adjustmet_date: ", adjustment_date
        print "adjustment_id: ", adjustment.id

        return adjustment


    def add_note(self, note, user=''):
        '''

        Adds a note to an account

        '''
        print "adding note to account id: ", self.id
 
        note = AccountNote(account=self, note=note, username=user)

        note.save()

        print "note_id: ", note.id

        return note

    @property
    def reading(self):
        '''

        Property to get the most recent reading for the Account

        '''
        latest_reading = self.get_current_reading()

        return latest_reading

    def get_current_reading(self, period=None):
        '''

        Returns the current_reading value from the account's latest meter read

        '''
        if period is None:
            period = Config.objects.get(name='active_period').value
        
        bs = BillingSchedule.objects.get(pk=period)
        meter = self.meter

        reads = MeterRead.objects.filter(meter=meter,account=self)
        
        if not reads: #if the current period does not return a read, get latest read for account only
            reads = MeterRead.objects.filter(account=self)

        latest_read = reads.latest('id')
        print "latest_read.current_reading: ", latest_read.current_reading
        return latest_read.current_reading

    def get_previous_reading(self, period=None):
        '''

        Returns the previous_reading value from the account's latest meter read

        '''

        if period is None:
            period = Config.objects.get(name='active_period').value
        
        bs = BillingSchedule.objects.get(pk=period)

        reads = MeterRead.objects.filter(billing_schedule=bs,account=self)
        latest_read = reads.latest('id')
        return latest_read.previous_reading

    def get_bill(self, period=None):
        ''' 

        Returns the bill for a given period. Default is active period.

        '''

        if period is None:
            period = Config.objects.get(name='active_period').value

        bs = BillingSchedule.objects.get(pk=period)


        bill = Bill.objects.filter(billing_schedule=bs,account=self)

        customer_name = self.customer.last_name + ", " + self.customer.first_name
        address = self.address.address1

        if bill.count() == 1:
            return bill.get() #return bill

        elif bill.count() > 1:
            raise AccountException("More than 1 bill for Account: %s , Address: %s and BillingSchedule: %s", customer_name , address, str(bs))
            
        
        return None

    def update(self, *args, **kwargs):       
        try:
            super(Account, self).save(*args, **kwargs) # Call the "real" save() method.

        except Exception, e:
            print "account update failed", e
            raise e


class AccountMeter(CoreModel):
    """
    AccountMeter maps an account to any number of Meters.
    But only one meter can be active at a time
    """
    account = models.ForeignKey('Account', db_column='account_id')
    meter = models.ForeignKey('Meter', db_column='meter_id')
    status = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'account_meter'
        unique_together = ('account', 'meter')

    def __unicode__(self):
        return u'-'#.join([unicode(self.account),unicode(self.meter)])



class AccountType(CoreModel):
    description = models.TextField(db_column='description', unique=True)
    rate = models.ForeignKey('Rate', db_column='rate_id', unique=True)
    
    class Meta:
        db_table = 'account_type'

    def __unicode__(self):
        return self.description

    def save(self, *args, **kwargs):
        try:
            self.rate = Rate.objects.get(rate=self.description)
            super(AccountType, self).save(*args, **kwargs) # Call the "real" save() method.
        except Exception, e:
            print e
            return


class Address(CoreModel):
    address1 = models.TextField("Complete address")
    address2 = models.TextField("Block number", blank=True)
    address3 = models.TextField("Lot number", blank=True)
    address4 = models.TextField("Area", blank=True)
    zip_code = models.BigIntegerField(blank=True)
    
    class Meta:
        verbose_name_plural = "addresses"
        db_table = 'address'
        unique_together = ('address1', 'address2', 'address3', 'address4', 'zip_code')

    def __unicode__(self):
        return ",".join([self.address1 , self.address2, self.address3, self.address4]) 


class AccountNote(CoreModel):

    account = models.ForeignKey('Account', db_column='account_id')
    note = models.TextField()
    username = models.TextField()

    class Meta:
        db_table = 'account_note'
    
    


class Adjustment(CoreModel):
    financial_transaction = models.OneToOneField('FinancialTransaction', db_column='financial_transaction_id')    
    description = models.TextField(blank=True)
    type = models.TextField(blank=False) #credit, debit 
    amount = models.DecimalField(decimal_places=2, max_digits=11, db_column='amount')
    adjustment_date = models.DateField(db_column='adjustment_date')
    account = models.ForeignKey('Account', db_column='account_id')
    
    class Meta:
        db_table = 'adjustment'

    @transaction.commit_manually        
    def save(self, *args, **kwargs):
        if not self.adjustment_date: 
            self.adjustment_date = now().date()

        try:
            previous_transaction = self.account.financialtransaction_set.latest('id')
            previous_balance = previous_transaction.balance
        except FinancialTransaction.DoesNotExist, e:
            previous_balance = Decimal('0.0')
        if self.type in ['debit', 'reconnection_fee']:
            print 'self type is debit: ', self.type
            balance = previous_balance + self.amount
        else:
            print 'self type is not debit: ', self.type
            balance = previous_balance - self.amount
        try:
            print 'before financial transaction', self.account.id, self.amount, self.type, balance, self.adjustment_date
            self.financial_transaction = FinancialTransaction.objects.create(
                account_id=self.account.id,
                amount = self.amount,
                type = self.type,
                balance = balance,
                transaction_date= self.adjustment_date)
            print 'self financial_transaction', self.financial_transaction
            super(Adjustment, self).save(*args, **kwargs)
            print 'after super adjustment'
            
        except Exception, e:
            print 'exception', e
            transaction.rollback()
            raise e
        else:
            transaction.commit()


class BillingSchedule(CoreModel):
    reading_start_date = models.DateField(db_column='reading_start_date')
    reading_end_date = models.DateField(db_column='reading_end_date')
    start_date = models.DateField(db_column='start_date')
    end_date = models.DateField(db_column='end_date')
    status = status = models.TextField(blank=True, default='inactive')

    class Meta:
        db_table = 'billing_schedule'
        unique_together = ('start_date', 'end_date')

    def __unicode__(self):
        return unicode(self.start_date.strftime("%b %d, %Y")) + u" - " + unicode(self.end_date.strftime("%b %d, %Y"))

    def due_date(self):
        from datetime import timedelta
        days_due = int(Config.objects.get(name='days_due').value)
        due_date = self.start_date + timedelta(days_due)
        return due_date

    @property
    def previous(self):
        return self.get_previous_by_start_date()

    @property
    def next(self):
        return self.get_next_by_start_date()



class Bill(CoreModel):
    """
    A bill is unique based on schedule, account
    Must provide the following:
    account
    billing_schedule

    """
    financial_transaction = models.OneToOneField('FinancialTransaction', db_column='financial_transaction_id')
    billing_schedule = models.ForeignKey('BillingSchedule', db_column='billing_schedule_id')
    account = models.ForeignKey('Account', db_column='account_id')
    meter_read = models.ForeignKey('MeterRead', db_column='meter_read_id')
    bill_date = models.DateField(db_column='bill_date')
    due_date = models.DateField(db_column='due_date')
    previous_balance = models.DecimalField(decimal_places=2, max_digits=11, db_column='previous_balance')
    current_charge = models.DecimalField(decimal_places=2, max_digits=11, db_column='current_charge', editable=False)
    penalty_amount = models.DecimalField(decimal_places=2, max_digits=11, db_column='penalty_amount')
    amount_due = models.DecimalField(decimal_places=2, max_digits=11, db_column='amount_due')
    tracking_number = models.TextField(blank=True)

    audit_log = AuditLog()
    
    class Meta:
        db_table = 'bill'
        unique_together = ('billing_schedule', 'account')

    def __unicode__(self):
        return u'-'.join([unicode(self.account), unicode(self.billing_schedule), unicode(self.amount_due)])

    def update(self, *args, **kwargs):       
        try:
            super(Bill, self).save(*args, **kwargs) # Call the "real" save() method.

        except Exception, e:
            print "bill update failed", e
            raise e

    @transaction.commit_manually
    def save(self,  business_date=None, *args, **kwargs):
        """
        Calculate current_charge
        Get previous_balance
        Get penalty_amount (sum of penalty transactions during penalty_period)
        """
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        try:
            previous_transaction = self.account.financialtransaction_set.latest('id')
            self.previous_balance = previous_transaction.balance
        except FinancialTransaction.DoesNotExist, e:
            self.previous_balance = Decimal('0.0')
        """
        try:
            self.reconnection_fees = self.account.reconnection_fees
        except:
            self.reconnection_fees = Decimal('0.0')
        """

        try:
            
            # get business date and tracking number
            if business_date == None:                
                business_date = Config.objects.get(name='business_date').value
            
            tnconfig = Config.objects.get(name='tracking_number')
            zeroes = int(Config.objects.get(name='trn_zeroes').value)
            self.save_read_charges()
            self.save_overdue_penalty()
            self.current_charge = sum([i.amount for i in self.meter_read.readcharge_set.all()])
            self.penalty_amount = sum([i.amount for i in self.billing_schedule.penalty_set.filter(account_id=self.account.id).all()])
            self.amount_due = self.current_charge + self.penalty_amount + self.previous_balance# + self.reconnection_fees
            #self.bill_date = self.billing_schedule.end_date
            self.bill_date = datetime.strptime(business_date,'%Y-%m-%d')
            #self.due_date = self.bill_date + timedelta(days=19)
            first_day, last_day = get_month_day_range(self.bill_date)
            print "last_day: ", last_day
            print "first_day: ", first_day
            self.due_date = last_day + timedelta(days=-1)

            self.financial_transaction = FinancialTransaction.objects.create(
                    account_id=self.account.id,
                    amount = self.current_charge + self.penalty_amount,
                    balance = self.amount_due,
                    type = self._meta.db_table,
                    transaction_date = self.bill_date)
            
            
            # compose bill tracking number  
            self.tracking_number = str(business_date).replace('-','') + "-" + str(tnconfig.value).zfill(zeroes)
            tnconfig.value = str(int(tnconfig.value) + 1) # increase config tracking number
            tnconfig.save()


        except Exception, e:
            print "Bill Rollback", e
            transaction.rollback()
            raise e
        else:                                         
            super(Bill, self).save(*args, **kwargs) # Call the "real" save() method.
            transaction.commit()

    def usage_to_amount(self, usage=Decimal('0.00')):
        """
        Convert/calculate consumption to amount based on defined rate charges
        """

        rate_charges = self.account.account_type.rate.ratecharge_set.all()
        amount = Decimal('0.0')
        
        #assume incremental
        for rate_charge in rate_charges:
            if rate_charge.read_value_end < usage:
                #print (rate_charge.read_value_end - rate_charge.read_value_start), charge.amount
                if rate_charge.type == 'Constant':
                    amount += rate_charge.amount
                else:
                    amount += (rate_charge.read_value_end - rate_charge.read_value_start) *  rate_charge.amount
            else:
                #print usage - rate_charge.read_value_start, rate_charge.amount
                if rate_charge.type == 'Constant':
                    amount += rate_charge.amount
                else:
                    amount += (usage - rate_charge.read_value_start) * rate_charge.amount
                break
        return amount

    def save_overdue_penalty(self):
        print "overdue save"
        try:
            print "got here"
            if self.billing_schedule.penalty_set.filter(
                    account_id=self.account.id,
                    type='overdue').exists():
                    print "not empty, exiting", self.billing_schedule.penalty_set.filter(
                        account_id=self.account.id,
                        type='overdue').all()
                    return
        except Penalty.DoesNotExist, e:
            print "Penalty does not exist for this account"
            pass

        #check if there is a previous balance
        try:
            print "WARNING: PENALTY is calculated for now by checking latest balance"
            previous_transaction = self.account.financialtransaction_set.latest('id')
            previous_balance = previous_transaction.balance
            if previous_balance > Decimal('0.0'):
                Penalty.objects.create(
                    billing_schedule = self.billing_schedule, 
                    account_id = self.account.id, 
                    type = 'overdue',
                    amount = previous_balance * Decimal('0.05'),
                    penalty_date=now().date())
        except FinancialTransaction.DoesNotExist, e:
            pass

    def save_read_charges(self):
        """
        Insert ReadCharge to store breakdown of rates charges for a particular usage
        """
        rate_charges = self.account.account_type.rate.ratecharge_set.all()
        amount = Decimal('0.0')
        #usage = self.meter_read.usage
        usage, meterread = self.account.get_meter_reads_usage(period=self.billing_schedule.pk)

        #self.meter_read_id = int(meterread.pk)

        read_charges = []
        for rate_charge in rate_charges:

            if rate_charge.read_value_end < usage:
                if rate_charge.type == 'Constant':
                    read_charges.append(
                        ReadCharge(meter_read_id = self.meter_read_id, 
                            rate_charge_id = rate_charge.id,
                            quantity = (rate_charge.read_value_end - 
                                        rate_charge.read_value_start),
                            amount = rate_charge.amount))
                else:
                    read_charges.append(
                        ReadCharge(meter_read_id = self.meter_read_id, 
                            rate_charge_id = rate_charge.id,
                            quantity = (rate_charge.read_value_end - 
                                        rate_charge.read_value_start),
                            amount = (rate_charge.read_value_end - 
                                        rate_charge.read_value_start) *  
                                        rate_charge.amount))
            else:
                #print usage - rate_charge.read_value_start, rate_charge.amount
                if rate_charge.type == 'Constant':
                    read_charges.append(
                        ReadCharge(meter_read_id = self.meter_read_id, 
                            rate_charge_id = rate_charge.id,
                            quantity = max(Decimal('0.0'), (usage - rate_charge.read_value_start)),
                            amount = rate_charge.amount))
                else:
                    read_charges.append(
                        ReadCharge(meter_read_id = self.meter_read_id, 
                            rate_charge_id = rate_charge.id,
                            quantity = max(Decimal('0.0'), (usage - rate_charge.read_value_start)),
                            amount = max(Decimal('0.0'), (usage - rate_charge.read_value_start)) * 
                                rate_charge.amount))

        ReadCharge.objects.bulk_create(read_charges)


    def create_deleted_copy(self,deletor='admin'):
        deleted = BillDeleted()
        for field in self._meta.fields:
            setattr(deleted,field.name, getattr(self,field.name))
        deleted.deleted_by = deletor
        deleted.save()

        

class BillDeleted(CoreModel):
    """
    This model stores archived copies of deleted Bills.

    """
    financial_transaction = models.OneToOneField('FinancialTransaction', db_column='financial_transaction_id')
    billing_schedule = models.ForeignKey('BillingSchedule', db_column='billing_schedule_id')
    account = models.ForeignKey('Account', db_column='account_id')
    meter_read = models.ForeignKey('MeterRead', db_column='meter_read_id')
    bill_date = models.DateField(db_column='bill_date')
    due_date = models.DateField(db_column='due_date')
    previous_balance = models.DecimalField(decimal_places=2, max_digits=11, db_column='previous_balance')
    current_charge = models.DecimalField(decimal_places=2, max_digits=11, db_column='current_charge', editable=False)
    penalty_amount = models.DecimalField(decimal_places=2, max_digits=11, db_column='penalty_amount')
    amount_due = models.DecimalField(decimal_places=2, max_digits=11, db_column='amount_due')
    tracking_number = models.TextField(blank=True)
    deleted_by = models.TextField(db_column='deleted_by', blank=False, editable=False)
    deleted_on = models.DateTimeField(default=now, editable=False)

    class Meta:
        verbose_name_plural = "deleted bills"
        db_table = 'bill_deleted'
        #   unique_together = ('billing_schedule', 'account')

    def __unicode__(self):
        return u'-'.join([unicode(self.account), unicode(self.billing_schedule), unicode(self.amount_due)])

    def update(self, *args, **kwargs):       
        try:
            super(BillDeleted, self).save(*args, **kwargs) # Call the "real" save() method.

        except Exception, e:
            print "deleted bill update failed", e
            raise e

        
class Penalty(CoreModel):
    billing_schedule = models.ForeignKey('BillingSchedule', db_column='billing_schedule_id')
    account = models.ForeignKey('Account', db_column='account_id')
    type = models.TextField(db_column='type', editable=False)
    description = models.TextField(blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=11, db_column='amount')
    penalty_date = models.DateField(db_column='penalty_date')
    status = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "penalties"
        db_table = 'penalty'


class Customer(CoreModel):
    last_name = models.TextField(db_column='last_name')
    first_name = models.TextField(db_column='first_name')
    middle_name = models.TextField(db_column='middle_name')
    email_address = models.TextField(db_column='email_address', blank=True)
    phone1 = models.TextField(blank=True)
    phone2 = models.TextField(blank=True)
    phone3 = models.TextField(blank=True)
    
    class Meta:
        db_table = 'customer'
        ordering = ['last_name']

    def __unicode__(self):
        return self.last_name + u', ' + self.first_name + u' ' + self.middle_name


class FinancialTransaction(CoreModel):
    """
    Debit (Charge) and Credit (Payment) for Account should always be recorded here
    """
    type = models.TextField(db_column='type', editable=False)
    account = models.ForeignKey('Account', db_column='account_id', editable=False)
    amount = models.DecimalField(max_digits=11, decimal_places=2, editable=False)
    balance = models.DecimalField(max_digits=11, decimal_places=2, editable=False)
    transaction_date = models.DateField(blank=False)
    
    audit_log = AuditLog()

    class Meta:
        db_table = 'financial_transaction'
        ordering = ['account']

    def __unicode__(self):
        return '-'.join([unicode(self.account), self.type, unicode(self.amount)])  

    def is_credit(self):
        if self.type in ['posted_payment', 'refund', 'credit','bill_deletion']:
            return True


class MeterReadException(Exception):
    pass


class MeterRead(CoreModel):
    meter = models.ForeignKey('Meter', db_column='meter_id')
    account = models.ForeignKey('Account', db_column='account_id')
    billing_schedule = models.ForeignKey('BillingSchedule', db_column='billing_schedule_id')
    read_date = models.DateField(db_column='read_date')
    read_time = models.TimeField(db_column='read_time')
    previous_reading = models.DecimalField(decimal_places=3, max_digits=11, db_column='previous_reading', editable=False)
    current_reading = models.DecimalField(decimal_places=3, max_digits=11, db_column='current_reading')
    usage = models.DecimalField(decimal_places=2, max_digits=11, editable=False)
    status = models.TextField(default='new')
    remarks = models.TextField(default='')

    audit_log = AuditLog()
    
    class Meta:
        db_table = 'meter_read'
        unique_together = ('account', 'meter', 'billing_schedule', 'read_date')

    def __unicode__(self):
        return u'-'.join([unicode(self.meter), unicode(self.read_date), unicode(self.usage)])

    def save(self, *args, **kwargs):
        #TODO:
        #Check if there is already a meter_read for a particular meter in the billing schedule where read date falls.
        #Add status of for the read

        
        #billing_schedule = BillingSchedule.objects.get(reading_start_date__lte = self.read_date, start_date__gt = self.read_date)
        print "billing_schedule: ", self.billing_schedule
        billing_schedule = self.billing_schedule
        try:
            if self.meter.meterread_set.exists():
                last_meter_read = self.meter.meterread_set.latest('previous_reading')
                bill = self.account.get_bill(period=billing_schedule.pk)
                if bill:   
                    #raise MeterReadException('Meter read %d already exists for billing schedule %d' %(last_meter_read.id, billing_schedule.id))
                    raise MeterReadException('Bill %d already exists for billing schedule %s. Cannot accept more reads.. ' %(bill.id, str(billing_schedule)))
                else:
                    self.previous_reading = self.meter.meterread_set.latest('previous_reading').current_reading
                
                
            else:
                
                if not self.previous_reading:
                    self.previous_reading = Decimal('0.0')

            self.usage = Decimal(self.current_reading) - Decimal(self.previous_reading)
            if self.usage < 0:
                print "Negative usage is not permitted  ----- " + str(self.usage)  + " -- meter id: " + str(self.meter)              
                self.usage = Decimal('0.0')
                #self.previous_reading = self.current_reading
                self.current_reading = self.previous_reading
                
                #raise MeterReadException('Negative usage not permitted')

            super(MeterRead, self).save(*args, **kwargs) # Call the "real" save() method.

        except Exception, e:
            print "meter read save failed", e
            raise e


    def update(self, *args, **kwargs):       
        try:
            super(MeterRead, self).save(*args, **kwargs) # Call the "real" save() method.

        except Exception, e:
            print "meter read update failed", e
            raise e

class Meter(CoreModel):
    meter_uid = models.TextField(db_column='meter_uid', unique=True)
    type = models.TextField(blank=True)
    date_installed = models.DateField(db_column='date_installed')
    status = models.TextField(blank=True)
    
    class Meta:
        db_table = 'meter'

    def __unicode__(self):
        return unicode(self.meter_uid) + u'-' + unicode(self.id) + self.type

    def activate(self, *args, **kwargs):
        """
        Activate the Meter by initializing the first MeterRead
        """
        try:            
            if self.meterread_set.exists():
                pass
        except MeterRead.DoesNotExist, e:
            print "no meterreads yet, activating together with the account"
            #'Activate' the meter by inserting a meterread entry with 0 previous and current reading
            mr = MeterRead(meter=self, current_reading=Decimal('0.0'), 
                        read_date = now().date(), read_time = now().time(),
                        )
            self.status = 'active'
            mr.save()
            self.save()
            
    @property
    def latest_read(self):
        self.meterread_set.latest('previous_reading').current_reading


class PostedPayment(CoreModel):
    financial_transaction = models.OneToOneField('FinancialTransaction', db_column='financial_transaction_id')
    payment = models.OneToOneField('Payment', db_column='payment_id')
    posted_date = models.DateField(db_column='posted_date')

    class Meta:
        db_table = 'posted_payment'

    @transaction.commit_manually        
    def save(self, *args, **kwargs):
        if not self.posted_date: 
            self.posted_date = now().date()

        try:
            previous_transaction = self.payment.account.financialtransaction_set.latest('id')
            previous_balance = previous_transaction.balance
        except FinancialTransaction.DoesNotExist, e:
            previous_balance = Decimal('0.0')
        try:
            self.financial_transaction = FinancialTransaction.objects.create(
                account_id=self.payment.account.id,
                amount = self.payment.amount,
                balance = previous_balance - self.payment.amount,
                type = self._meta.db_table,
                transaction_date= self.posted_date)
            self.payment.status = 'posted'
            self.payment.save()
            super(PostedPayment, self).save(*args, **kwargs)
        except Exception, e:
            transaction.rollback()
            raise e
        else:
            transaction.commit()


class Payment(CoreModel):
    """
    To handle penalties, must check if there are unpaid balances
    """   
    account = models.ForeignKey('Account', db_column='account_id')
    amount = models.DecimalField(decimal_places=2, max_digits=11, db_column='amount')
    remarks = models.TextField(blank=True)
    payment_date = models.DateField(db_column='payment_date')
    type = models.TextField(blank=True)
    status = models.TextField(blank=True, default="new")
    check_number = models.TextField(blank=True,default="")

    class Meta:
        db_table = 'payment'

    def save(self, *args, **kwargs):
        if not self.payment_date: 
            self.payment_date = now().date()
        super(Payment, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'-'.join([unicode(self.account), unicode(self.payment_date), 
                unicode(self.amount)])


class RateCharge(CoreModel):
    """
    Charge matrix for a particular Rate type.
    Depending on used resource (water, electricity), different charges apply
    """
    rate = models.ForeignKey('Rate', db_column='rate_id')
    type = models.TextField()
    sequence_number = models.IntegerField(db_column='sequence_number')
    read_value_start = models.DecimalField(decimal_places=2, max_digits=11, db_column='read_value_start')
    read_value_end = models.DecimalField(decimal_places=2, max_digits=11, db_column='read_value_end')
    amount = models.DecimalField(decimal_places=2, max_digits=11, db_column='amount')
    
    class Meta:
        db_table = 'rate_charge'
        ordering = ['type', 'read_value_start']

    def __unicode__(self):
        return u'-'.join([unicode(self.rate), self.type, 
                unicode(self.read_value_start), unicode(self.read_value_end), 
                unicode(self.amount)])
    

class Rate(CoreModel):
    description = models.TextField()
    
    class Meta:
        db_table = 'rate'

    def __unicode__(self):
        return unicode(self.description)


class ReadCharge(CoreModel):
    """
    Breakdown of the amount based on the usage in meter_read
    """
    rate_charge = models.ForeignKey('RateCharge', db_column='rate_charge_id')
    meter_read = models.ForeignKey('MeterRead', db_column='meter_read_id')
    quantity = models.DecimalField(decimal_places=2, max_digits=11, db_column='quantity')
    amount = models.DecimalField(decimal_places=2, max_digits=11, db_column='amount')
    
    class Meta:
        db_table = 'read_charge'

    def __unicode__(self):
        return u'-'.join([unicode(self.rate_charge), unicode(self.meter_read), 
                unicode(self.amount)])


class Notice(CoreModel):
    billing_schedule = models.ForeignKey('BillingSchedule', db_column='billing_schedule_id')
    account = models.ForeignKey('Account', db_column='account_id')
    amount = models.DecimalField(decimal_places=2, max_digits=11, db_column='amount')
    notice_date = models.DateField(db_column='notice_date')
    due_date = models.DateField(db_column='due_date')
    reconnection_fee = models.DecimalField(decimal_places=2, max_digits=11, db_column='reconnection_fee')
    
    class Meta:
        db_table = 'notice'



class FileRepo(CoreModel):

    file_name = models.TextField()
    file_path = models.TextField()
    file_type = models.TextField()
    file_description = models.TextField()
    generation_date = models.DateField(db_column='generation_date')
    business_date = models.DateField(db_column='business_date')
    reading_period =models.TextField()

    
    class Meta:
        db_table = 'filerepo'


class Task(CoreModel):

    name = models.TextField()           # name of task e.g. "Generating Bills"
    type = models.TextField()           # type of task "Bills, Notices"
    task_id = models.BigIntegerField(default=0)
    jobs_total = models.IntegerField(db_column='jobs_total', default=0)     # expected number of records to be processed by this task
    jobs_done = models.IntegerField(db_column='jobs_done', default=0)      # actual number of records processed
    status = models.TextField()         # 'pending', 'in progress', 'completed', 'failed'
    result = models.TextField()         # records processed, and records in error here
    description = models.TextField()    # task description (any)
    business_date = models.DateField(db_column='business_date')  # business_date executed
    reading_period =models.TextField()  # period executed
    deleted = models.BooleanField(default=False) # records here should not be deleted, just marked 

    
    class Meta:
        db_table = 'task'

def get_month_day_range(date):
    """
    For a date 'date' returns the start and end date for the month of 'date'.
 
    Month with 31 days:
    >>> date = datetime.date(2011, 7, 27)
    >>> get_month_day_range(date)
    (datetime.date(2011, 7, 1), datetime.date(2011, 7, 31))
 
    Month with 28 days:
    >>> date = datetime.date(2011, 2, 15)
    >>> get_month_day_range(date)
    (datetime.date(2011, 2, 1), datetime.date(2011, 2, 28))
    """
    from dateutil.relativedelta import relativedelta

    last_day = date + relativedelta(day=1, months=+1, days=-1)
    first_day = date + relativedelta(day=1)
    return first_day, last_day
