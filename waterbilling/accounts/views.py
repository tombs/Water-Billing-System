# -*- coding: utf-8 -*-
# Create your views here.
import json
from decimal import Decimal
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from eztables.views import DatatablesView
from .models import Account, Payment, Adjustment, PostedPayment, FinancialTransaction
from core.models import BillingSchedule, Bill, Address, Config, AccountNote
from core.views import login_required, ajax_view
from payments import forms as payform
from adjustments import forms as adjform
from datetime import datetime, date
from django.db.models import Sum, Max, F
from core.utils import UnicodeWriter

@login_required
class AccountListView(TemplateView):

    def get_queryset(self):
        qs = super(AccountListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(AccountListView, self).get_context_data(**kwargs)
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        business_date = Config.objects.get(name='business_date').value
        business_date = datetime.strptime(business_date,'%Y-%m-%d')
        business_date = business_date.strftime('%b %d, %Y')
        context['period'] = str(bs)
        context['usage'] = bs.reading_start_date.strftime("%b %d, %Y") + " - " + bs.reading_end_date.strftime("%b %d, %Y")
        context['business_date'] = business_date

        context['aggregate'] = Address.objects.values('address4').filter(
                id__in=Account.objects.annotate(
                        last_transaction_id=Max('financialtransaction')).values_list(
                            'last_transaction_id'), 
                        account__financialtransaction__balance__gt=0).annotate(
                        unc=Sum('account__financialtransaction__balance')).order_by('address4').all()
        context['aggregate_total'] = sum([i['unc'] for i in context['aggregate']])
        return context



@login_required
@ajax_view
class AccountDatatablesView(DatatablesView):
    queryset = FinancialTransaction.objects.filter(id__in=Account.objects.annotate(last_transaction_id=Max('financialtransaction')).values_list('last_transaction_id'))
    fields = (
        'account__id',
        '{account__customer__last_name}, {account__customer__first_name}', 
        'account__address__address4',
        'account__account_type__description',
        '{account__accountmeter__meter__meter_uid}',
        'account__status',
        'account__remarks',
        'balance'
        )

@login_required
class AccountDetailView(DetailView):

    model = Account
    context_object_name = 'account'
    payment_form_class = payform.PaymentForm
    adjustment_form_class = adjform.AdjustmentForm

    def get_context_data(self, **kwargs):
        print 'kwargs', kwargs
        print 'request', self.request
        context = super(AccountDetailView, self).get_context_data(**kwargs)
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        business_date = Config.objects.get(name='business_date').value
        business_date = datetime.strptime(business_date,'%Y-%m-%d')
        payment_date = business_date.strftime("%m/%d/%Y")
        business_date = business_date.strftime('%b %d, %Y')
        context['period'] = str(bs)
        context['usage'] = bs.reading_start_date.strftime("%b %d, %Y") + " - " + bs.reading_end_date.strftime("%b %d, %Y")
        context['business_date'] = business_date
        context['payment_date'] = payment_date
        if context['account'].bill_set.exists():
            context['bill_detail'] = context['account'].bill_set.latest('bill_date')
            context['read_charges'] = context['bill_detail'].meter_read.readcharge_set.order_by('id').all()
        else:
            context['bill_detail'] = []
            context['read_charges'] = []  
        context['payment'] = context['account'].payment_set.all()
        context['payment_form'] = self.payment_form_class()
        context['adjustment_form'] = self.adjustment_form_class()
        #context['now'] = timezone.now()
        return context

@login_required
@ajax_view
class AccountWithBalanceDatatablesView(DatatablesView):
    ''' need to filter all accounts with balance > 0, and return the fields below
        also need to sum the balances per phase/area
    '''

    queryset = FinancialTransaction.objects.filter(id__in=Account.objects.annotate(last_transaction_id=Max('financialtransaction')).values_list('last_transaction_id'), balance__gt=0, account__status='for disconnection').order_by(*['account__address__address4','account__address__address2','account__address__address3'])
    fields = (
        'account__id',
        '{account__customer__last_name}, {account__customer__first_name}', 
        'account__address__address4', # phase
        'account__address__address2', # block
        'account__address__address3', # lot
        'balance',
        'account__status',
        'account__remarks',              
        )

    # def get_queryset(self):
    #     qs = super(AccountWithBalanceDatatablesView, self).get_queryset()
        
    #     #qs = qs.annotate(last_transaction_id=Max('financialtransaction')).filter(financialtransaction__balance__gt=0)
    #     print "qs", qs.query
    #     return qs

    # def process_dt_response(self, data):
    #     res = super(AccountWithBalanceDatatablesView, self).process_dt_response(data)
    #     print "qs1", self.get_queryset().values(*self.get_db_fields()).query
    #     return res

@login_required
class AccountWithBalanceListPrintView(ListView):
    ''' need to filter all accounts with balance > 0, and return the fields below
        also need to sum the balances per phase/area
    '''

    queryset =  FinancialTransaction.objects.filter(id__in=Account.objects.annotate(last_transaction_id=Max('financialtransaction')).values_list('last_transaction_id'), balance__gt=0)

    def get_context_data(self, **kwargs):
        context = super(AccountWithBalanceListPrintView, self).get_context_data(**kwargs)
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        business_date = Config.objects.get(name='business_date').value
        business_date = datetime.strptime(business_date,'%Y-%m-%d')
        business_date = business_date.strftime('%b %d, %Y')
        context['period'] = str(bs)
        context['usage'] = bs.reading_start_date.strftime("%b %d, %Y") + " - " + bs.reading_end_date.strftime("%b %d, %Y")
        context['business_date'] = business_date
        context['aggregate'] = Address.objects.values('address4').filter(
                id__in=Account.objects.annotate(
                        last_transaction_id=Max('financialtransaction')).values_list(
                            'last_transaction_id'), 
                        account__financialtransaction__balance__gt=0).annotate(
                        unc=Sum('account__financialtransaction__balance')).order_by('address4').all()
        context['aggregate_total'] = sum([i['unc'] for i in context['aggregate']])
        return context

@login_required
class AccountWithBalanceCsvView(DetailView):

    queryset = FinancialTransaction.objects.filter(
            id__in=Account.objects.annotate(last_transaction_id=Max(
                'financialtransaction')).values_list(
                'last_transaction_id'), 
                balance__gt=0).values(
            'account__id',
            'account__customer__last_name',
            'account__customer__first_name',
            'account__address__address1', 
            'account__address__address4',
            'balance',
            'account__status',
            'account__remarks',  ).order_by('account__address__address1')
    
    def get(self,request, *args, **kwargs):
        #https://docs.djangoproject.com/en/dev/howto/outputting-csv/
        data = self.queryset.all()
        header = ['account_id','customer','balance','address','phase','status', 'remarks']
        kwargs['content_type'] = 'text/csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="withbalance.csv"'
        csv_data = UnicodeWriter(response)
        csv_data.writerow(header)
        for row in data:
            csv_data.writerow([
                unicode(row['account__id']),
                row['account__customer__last_name'] + u',' + row['account__customer__first_name'],
                unicode(row['balance']),
                row['account__address__address1'],
                row['account__address__address4'],
                row['account__status'],
                row['account__remarks'],
            ])
        return response


@login_required
class AccountDisconnectedListView(ListView):
    ''' need to filter all accounts with status = "disconnected" '''

    model = Account
    queryset = Account.objects.filter(status="disconnected")
    
    context_object_name = 'account_list'


@login_required
class AccountDisconnectedDatatablesView(DatatablesView):
    ''' need to filter all accounts with status = "disconnected" '''
    queryset = FinancialTransaction.objects.filter(id__in=Account.objects.filter(status="disconnected").annotate(last_transaction_id=Max('financialtransaction')).values_list('last_transaction_id'))
    fields = (
        'account__id',
        '{account__customer__last_name}, {account__customer__first_name}', 
        'account__address__address4',
        'balance',
        'account__status',
        'account__remarks',              
        )

    
    


@login_required
class AccountCollectionListView(TemplateView):
    ''' need to compute all payments made since bill date, but segregate between posted payment date and 
    payment date, and show all fields below '''

    #queryset = []
    context_object_name = 'account_list'

    def get_context_data(self, **kwargs):
        context = super(AccountCollectionListView, self).get_context_data(**kwargs)
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        business_date = Config.objects.get(name='business_date').value
        business_date = datetime.strptime(business_date,'%Y-%m-%d')
        business_date = business_date.strftime('%b %d, %Y')
        context['period'] = str(bs)
        context['usage'] = bs.reading_start_date.strftime("%b %d, %Y") + " - " + bs.reading_end_date.strftime("%b %d, %Y")
        context['business_date'] = business_date
        data_list = []        
        #for account in Account.objects.all():
        #    if not account.latest_bill:
        #        continue
        #        
        #    data = {}
        #    latest_bill = account.latest_bill.__dict__
        #    data['address1'] = account.address.address1
        #    data['pk'] = account.pk
        #    data['customer'] = account.customer
        #    data['bill_date'] = latest_bill['bill_date']
        #    data['previous_balance'] = latest_bill['previous_balance']
        #    data['current_charge'] = latest_bill['current_charge'] 
        #    data['penalty_amount'] = latest_bill['penalty_amount'] 
        #    data['amount_due'] = latest_bill['amount_due']
        #    data['total_posted_payment'] = account.total_posted_payment
        #    data['latest_balance'] = account.latest_balance
        #    data_list.append(data)
        #
        aggregate = dict(Address.objects.values_list('address4').filter(
                    account__financialtransaction__type__in=['posted_payment']).annotate(
                    col=Sum('account__financialtransaction__amount')).order_by(
                    'address4').all())
        for addy in Address.objects.values_list('address4').annotate().all():
            if addy[0] in aggregate:
                continue
            aggregate[addy[0]] = Decimal('0.0')

        context['aggregate'] = [{'address4': i, 'col':aggregate[i]}  for i in aggregate]
        context['aggregate_total'] = sum([i['col'] for i in context['aggregate']])
        context['account_list'] = data_list
        return context

        
@login_required
class AccountCollectionCsvView(DetailView):
    
    def get(self,request, *args, **kwargs):
        #https://docs.djangoproject.com/en/dev/howto/outputting-csv/
        header = ['Address','Customer','Bill Date','Previous Balance','Current Charge','Penalty', 'Amount Due', 'Reconnection Fees', 'Posted Payments', 'Collectibles']
        kwargs['content_type'] = 'text/csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="collection.csv"'
        csv_data = UnicodeWriter(response)
        csv_data.writerow(header)

        data_list = []        
        for account in Account.objects.all():
            if not account.latest_bill:
                continue
                
            data = {}
            latest_bill = account.latest_bill.__dict__
            csv_data.writerow([
            account.address.address1,
            unicode(account.customer),
            unicode(latest_bill['bill_date']),
            unicode(latest_bill['previous_balance']),
            unicode(latest_bill['current_charge']), 
            unicode(latest_bill['penalty_amount']), 
            unicode(latest_bill['amount_due']),
            unicode(account.reconnection_fees),
            unicode(account.total_posted_payment),
            unicode(account.latest_balance)
            ])

        return response



@login_required
@ajax_view
class AccountSetStatusActiveView(DetailView):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        account = self.model.objects.get(id = kwargs.get('pk'))
        
        try:
            account.status = 'active'
            account.save()
            data = {'status': 200, 'data': account.status, 'msg': 'Status set to ACTIVE' }
            status = 200
        except Exception, e:
            data = {'status': 200, 'data': account.status, 'msg': 'Unable to Status set to ACTIVE' }
            status = 400

        return self.render_to_json_response(data, status=status)

@login_required
@ajax_view
class AccountSetStatusInactiveView(DetailView):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        account = self.model.objects.get(id = kwargs.get('pk'))
        
        try:
            account.status = 'inactive'
            account.save()
            data = {'status': 200, 'data': account.status, 'msg': 'Status set to INACTIVE' }
            status = 200
        except Exception, e:
            data = {'status': 200, 'data': account.status, 'msg': 'Unable to Status set to INACTIVE' }
            status = 400

        return self.render_to_json_response(data, status=status)

@login_required
@ajax_view
class AccountSetStatusDisconnectedView(DetailView):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        account = self.model.objects.get(id = kwargs.get('pk'))
        
        try:
            account.status = 'disconnected'
            account.save()
            data = {'status': 200, 'data': account.status, 'msg': 'Status set to DISCONNECTED' }
            status = 200
        except Exception, e:
            data = {'status': 200, 'data': account.status, 'msg': 'Unable to Status set to DISCONNECTED' }
            status = 400

        return self.render_to_json_response(data, status=status)


@login_required
@ajax_view
class AccountSetStatusForDisconnectionView(DetailView):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        account = self.model.objects.get(id = kwargs.get('pk'))
        
        try:
            account.status = 'for disconnection'
            account.save()
            data = {'status': 200, 'data': account.status, 'msg': 'Status set to FOR DISCONNECTION' }
            status = 200
        except Exception, e:
            data = {'status': 200, 'data': account.status, 'msg': 'Unable to Status set to FOR DISCONNECTION' }
            status = 400

        return self.render_to_json_response(data, status=status)



@login_required
@ajax_view
class NoteAddView(DetailView):

    model = AccountNote
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def post(self, request, *args, **kwargs):
        print "This POST", request.POST
        request = request.POST
        account = Account.objects.get(pk=request.get('account'))
        note = request.get('note')
        user = request.get('user')
       
         
        try:
            note = account.add_note(note=note,user=user)
            print "Done with Add Account Note"

            data = {'status': 200, 'data': note.note, 'msg': 'Added new note with ID: ' + str(note.id)}
            status = 200
        except Exception, e:
            print "e: ", str(e)
            data = {'status': 200, 'msg': 'Unable to add note with : ' + request.get('note') }
            status = 400

        return self.render_to_json_response(data, status=status)