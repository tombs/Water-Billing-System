# -*- coding: utf-8 -*-
from decimal import Decimal
from django.http import Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from inspect import isfunction
from .models import Account, Payment, Adjustment, PostedPayment, FinancialTransaction
from core.models import BillingSchedule, Bill, Address, Config
from django.db.models import Sum, Max
from django.views.generic import TemplateView
from django.core.serializers.json import json, DjangoJSONEncoder
from datetime import datetime


class _cbv_decorate(object):
    def __init__(self, dec):
        self.dec = method_decorator(dec)

    def __call__(self, obj):
        obj.dispatch = self.dec(obj.dispatch)
        return obj

def patch_view_decorator(dec):
    def _conditional(view):
        if isfunction(view):
            return dec(view)

        return _cbv_decorate(dec)(view)

    return _conditional


login_required = patch_view_decorator(login_required)

@patch_view_decorator
def ajax_view(view):
    def _inner(request, *args, **kwargs):
        if request.is_ajax():
            return view(request, *args, **kwargs)
        else:
            raise Http404

    return _inner

@login_required
class DashboardView(TemplateView):

    def get_queryset(self):
        qs = super(DashboardView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        business_date = Config.objects.get(name='business_date').value
        business_date = datetime.strptime(business_date,'%Y-%m-%d')
        business_date = business_date.strftime('%b %d, %Y')
        context['period'] = str(bs)
        context['usage'] = bs.reading_start_date.strftime("%b %d, %Y") + " - " + bs.reading_end_date.strftime("%b %d, %Y")
        context['business_date'] = business_date

        uncollected = Address.objects.values('address4').filter(
                id__in=Account.objects.annotate(
                        last_transaction_id=Max('financialtransaction')).values_list(
                            'last_transaction_id'), 
                        account__financialtransaction__balance__gt=0).annotate(
                        unc=Sum('account__financialtransaction__balance')).order_by('address4').all()
        context['uncollected_total'] = sum([i['unc'] for i in uncollected])
        context['uncollected'] = json.dumps(list(uncollected), cls=DjangoJSONEncoder)

        collected = Address.objects.values('address4').filter(
                    account__financialtransaction__type__in=['posted_payment']).annotate(
                    col=Sum('account__financialtransaction__amount')).order_by(
                    'address4').all()

        context['collected_total'] = sum([i['col'] for i in collected])
        context['collected'] = json.dumps(list(collected), cls=DjangoJSONEncoder)
        
       

        aggregate = {}
        flot_stack = {'uncollected':[], 'collected':[]}
        for addy in Address.objects.values_list('address4').annotate().all():
            aggregate[addy[0]] = {"collected": Decimal('0.0'),"uncollected": Decimal('0.0')}

        for col in collected:
            aggregate[col['address4']]['collected'] = col['col']

        for col in uncollected:
            aggregate[col['address4']]['uncollected'] = col['unc']

        
        for k,v in sorted(aggregate.items()):
            flot_stack['uncollected'].append((k,v['uncollected']))
            flot_stack['collected'].append((k,v['collected']))


        context['flot_pie'] = json.dumps(aggregate, cls=DjangoJSONEncoder)
        context['flot_stack'] = json.dumps(flot_stack, cls=DjangoJSONEncoder)
        return context