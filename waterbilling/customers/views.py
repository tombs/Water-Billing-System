# -*- coding: utf-8 -*-
# Create your views here.
import json
from decimal import Decimal
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from eztables.views import DatatablesView
from .models import Customer, Account, Payment, Adjustment, PostedPayment, FinancialTransaction
from core.models import BillingSchedule, Bill, Address, Config, AccountNote
from core.views import login_required, ajax_view
from payments import forms as payform
from adjustments import forms as adjform
from datetime import datetime, date
from django.db.models import Sum, Max, F
from core.utils import UnicodeWriter

@login_required
class CustomerListView(TemplateView):

    def get_queryset(self):
        qs = super(CustomerListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(CustomerListView, self).get_context_data(**kwargs)
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        business_date = Config.objects.get(name='business_date').value
        business_date = datetime.strptime(business_date,'%Y-%m-%d')
        business_date = business_date.strftime('%b %d, %Y')
        context['period'] = str(bs)
        context['usage'] = bs.reading_start_date.strftime("%b %d, %Y") + " - " + bs.reading_end_date.strftime("%b %d, %Y")
        context['business_date'] = business_date
        return context

@login_required
@ajax_view
class CustomerDatatablesView(DatatablesView):
    model = Customer
    fields = (
        'id',
        'last_name',
        'first_name',
        'middle_name',
        'email_address',
        'phone1',
        'phone2',
        'phone3',
        'id',
        )

@login_required
class CustomerDetailView(DetailView):

    model = Customer
    #queryset = Account.objects.filter(account_type__account_type='Residential')
    context_object_name = 'customer_detail'

    def get_context_data(self, **kwargs):
        context = super(CustomerDetailView, self).get_context_data(**kwargs)
        print context
        #context['bill_detail'] = context['account_detail'].bill_set.latest('bill_date')
        #context['account'] = context['meter_read_detail'].meter.account_set.latest('last_updated')
        #context['now'] = timezone.now()
        return context

@login_required
@ajax_view
class CustomerAddView(DetailView):

    model = Customer

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def post(self, request, *args, **kwargs):
        print "This POST", request.POST
        request = request.POST
        print "request: ", str(request)

        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        business_date = Config.objects.get(name='business_date').value
        business_date = datetime.strptime(business_date,'%Y-%m-%d')

        last_name = request.get('last_name')
        first_name = request.get('first_name')
        middle_name = request.get('middle_name')
        email_address = request.get('email_address')
        phone1 = request.get('phone1')
        phone2 = request.get('phone2')
        phone3 = request.get('phone3')
      

        try:
            customer, created = Customer.objects.get_or_create(last_name = last_name, first_name = first_name, middle_name = middle_name,email_address = email_address, phone1 = phone1, phone2 = phone2, phone3 = phone3)
            print "customer: ", customer, created

            data = {'status': 200, 'data': meter.status, 'msg': 'Added new customer with ID: ' + str(customer.customer_uid)}
            status = 200
        except Exception, e:
            print "e: ", str(e)
            data = {'status': 200, 'data': meter.status, 'msg': 'Unable to add customer with : ' + request.get('last_name') }
            status = 400

        return self.render_to_json_response(data, status=status)

