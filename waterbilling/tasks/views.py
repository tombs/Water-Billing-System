# -*- coding: utf-8 -*-
# Create your views here.
import json
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from eztables.views import DatatablesView
from core.views import login_required, ajax_view
from .models import Bill, BillingSchedule, Account, FileRepo, Config, Task
from core.utils import get_business_date, business_date_to_date
from datetime import datetime

@login_required
class TaskListView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule    .objects.get(pk=period)
        business_date = Config.objects.get(name='business_date').value
        business_date = datetime.strptime(business_date,'%Y-%m-%d')
        business_date = business_date.strftime('%b %d, %Y')
        context['period'] = str(bs)
        context['usage'] = bs.reading_start_date.strftime("%b %d, %Y") + " - " + bs.reading_end_date.strftime("%b %d, %Y")
        context['business_date'] = business_date
        return context

@login_required
@ajax_view
class TaskDatatablesView(DatatablesView):
    model = Task
    fields = (
        'id',
        'name',
        'type',
        'jobs_done',
        'jobs_total',
        'status',
        'result',
        'created_by',
        )
        

@login_required
@ajax_view
class TaskProgressView(DetailView):

    model = Task
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "--- Task GET", args, kwargs
        #today = business_date_to_date() #timezone.now().date()
        #bs =  BillingSchedule.objects.get(start_date__lte=today, end_date__gte=today)
        today = datetime.strptime(Config.objects.get(name='business_date').value, '%Y-%m-%d').date()
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        task = kwargs.get('pk')
        try:
            if kwargs.get('pk'):
                task = self.model.objects.get(task_id = kwargs.get('pk'))
                data = {'status': task.status, 'jobs_done': str(task.jobs_done), 'jobs_total': str(task.jobs_total), 'msg':  str(task.task_id) + ' returned successfully'}
          
            status = 200
            print " -- got task : ", data

        except Exception, e:
            print "Exception", e
            data = {'status': 400, 'data': None, 'msg': u'Unable to get task ' + 
                            unicode(task) }
            status = 400

        return self.render_to_json_response(data, status=status)
