# -*- coding: utf-8 -*-
# Create your views here.
import json
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.forms.forms import NON_FIELD_ERRORS

from .models import Account, Payment, PostedPayment
from .forms import PaymentForm

from core.views import login_required, ajax_view
from decimal import Decimal

@login_required
@ajax_view
class PaymentView(CreateView):
    form_class = PaymentForm
    model = Account

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

	# def get(self, request, *args, **kwargs):
	# 	print "This POST"
	# 	form = self.form_class(initial=self.initial)
	# 	return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        
        form = self.form_class(request.POST)   
        if not request.user.has_perm('core.add_payment'):
            #http://stackoverflow.com/questions/8598247/how-to-append-error-message-to-form-non-field-errors-in-django
            form.full_clean()
            form._errors[NON_FIELD_ERRORS] = form.error_class(['User has no permission to add payment'])  

        if form.is_valid():
            print "form._errors", form._errors
            # <process form cleaned data>
            payment = Payment(**form.cleaned_data)
            payment.status = 'new'
            payment.save()
     

            if self.request.is_ajax():
                data = {
                    'data': {'pk': payment.pk},
                    'message': 'succesful'
                }
                return self.render_to_json_response(data)

            return HttpResponseRedirect('/accounts/' + str(payment.account.pk))

        else:
            if self.request.is_ajax():
                if form.errors:
                    print "payment errors", form.errors
                    result =  self.render_to_json_response(form.errors, status=400)
                return result
            return HttpResponseRedirect('/accounts/' + str(request.POST['account']))


@login_required
@ajax_view
class PaymentPostView(DetailView):

    model = Payment

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    
    def get(self, request, *args, **kwargs):
        try:
            payment = self.model.objects.get(id = kwargs.get('pk'))
            if request.user.has_perm('core.add_postedpayment'):
                payment.status='posted'
                payment.save()
                pp = PostedPayment(payment=payment)
                pp.save()
                data = {'status': 200, 'data': payment.id, 'msg': 'Payment ' + str(payment) + ' has been posted'}
                status = 200
                print "--> latest balance: ", payment.account.latest_balance
                print "--> account status: ", payment.account.status
                if payment.account.latest_balance <= Decimal('0.0') and payment.account.status=='for disconnection':
                    payment.account.status = 'active'
                    payment.account.save()
                    print "--> Account: %s  activated!!" % str(payment.account)

            else:
                data = {'status': 400, 'data': payment.id, 'msg': 'Unable update payment status ' }
                status=400
        except Exception, e:
            print "e: ", e
            data = {'status': 400, 'data': payment.id, 'msg': 'Unable update payment status ' }
            status=400

        return self.render_to_json_response(data, status=status)

@login_required
@ajax_view
class PaymentFailView(DetailView):

    model = Payment
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "HERE", args, kwargs
        try:
            payment = self.model.objects.get(id = kwargs.get('pk'))
            payment.status='failed'
            payment.save()
            data = {'status': 200, 'data': payment.id, 'msg': 'Payment ' + str(payment) + ' has been reverted'}
            status = 200
        except Exception, e:
            data = {'status': 200, 'data': payment.id, 'msg': 'Unable update payment status ' }
            status=400

        return self.render_to_json_response(data, status=status)
