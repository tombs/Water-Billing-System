# -*- coding: utf-8 -*-
# Create your views here.
import json
from django.utils import timezone
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect, HttpResponse
from .models import Account, Adjustment
from .forms import AdjustmentForm


#search this for ajax related info for django
# class AjaxableResponseMixin(object):

class AdjustmentView(CreateView):
    form_class = AdjustmentForm
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
        print "REQUEST", request.POST, request.is_ajax()
        print "FORM", form.is_valid(), form.errors
        if form.is_valid():
            # <process form cleaned data>
            print "cleaned_data", form.cleaned_data
            adjustment = Adjustment(**form.cleaned_data)
            adjustment.save()

            if self.request.is_ajax():
                data = {
                    'data': {'pk': adjustment.pk},
                    'message': 'succesful'
                }
                return self.render_to_json_response(data)

            return HttpResponseRedirect('/accounts/' + str(adjustment.account.pk))

        else:
            if self.request.is_ajax():
                result =  self.render_to_json_response(form.errors, status=400)
                print 'RESULT ', result
                return result
            return HttpResponseRedirect('/accounts/' + str(request.POST['account']))
