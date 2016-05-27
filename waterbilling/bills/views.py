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
from wkhtmltopdf.views import PDFTemplateView
from core.utils import get_business_date, business_date_to_date
from datetime import datetime

@login_required
class BillListView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(BillListView, self).get_context_data(**kwargs)
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
class BillDatatablesView(DatatablesView):
    model = Bill
    fields = (
        'id',
        '{account__customer__last_name}, {account__customer__first_name}',
        'account__address__address4',
        'bill_date',
        'due_date',
        'amount_due',
        'account__status',
        'account__remarks',
        )
        
@login_required
@ajax_view
class FileRepoDatatablesView(DatatablesView):
    model = FileRepo
    fields = (
        'id',
        'file_name',
        #'file_path',
        'generation_date',
        'file_name'
        )
        

@login_required
class BillDetailView(DetailView):

    model = Bill
    context_object_name = 'bill_detail'

    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        business_date = Config.objects.get(name='business_date').value
        business_date = datetime.strptime(business_date,'%Y-%m-%d')
        business_date = business_date.strftime('%b %d, %Y')
        context['period'] = str(bs)
        context['usage'] = bs.reading_start_date.strftime("%b %d, %Y") + " - " + bs.reading_end_date.strftime("%b %d, %Y")
        context['business_date'] = business_date
        context['account'] = context['bill_detail'].account
        context['read_charges'] = context['bill_detail'].meter_read.readcharge_set.order_by('id').all()
        #context['now'] = timezone.now()
        return context
        
@login_required
class PdfBillDetailView(PDFTemplateView):

    model = Bill
    context_object_name = 'bill_detail'
    cmd_options = settings.CMD_OPTIONS.get('BILLS',{})

    def get_context_data(self, **kwargs):
        context = super(PdfBillDetailView, self).get_context_data(**kwargs)
        context['bill_detail'] = self.model.objects.get(pk=context['pk'])
        self.object = context['bill_detail'] 
        context['account'] = context['bill_detail'].account
        context['read_charges'] = context['bill_detail'].meter_read.readcharge_set.order_by('id').all()
        #context['now'] = timezone.now()
        return context

@login_required
@ajax_view
class GenerateBillView(DetailView):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        #today = business_date_to_date() #timezone.now().date()
        #bs =  BillingSchedule.objects.get(start_date__lte=today, end_date__gte=today)
        today = datetime.strptime(Config.objects.get(name='business_date').value, '%Y-%m-%d').date()
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        account = None
        try:
            bill = 'Bills'   
            if kwargs.get('pk'):
                account = self.model.objects.get(id = kwargs.get('pk'))
                bill, created = account.generate_bill(business_date=str(today), period=period)
            else:
                print "----- creating a task.."
                task, task_created = Task.objects.get_or_create(name='Generate Bills PDF',type='bill', business_date=today)
                print "----- task created! : ", task_created
                if task_created:
                    print " --- generating bills "
                  
                    for account in self.model.objects.exclude(status='inactive'):
                        bill, created = account.generate_bill(business_date=str(today), period=period)
                    
                    print "-- finished generating bills.. "
                    task.status = 'pending'
                    task.created_by = request.user.username
                    task.save()
                    print "-- status has been saved! "


                else:
                    print "Cannot generate bills further, there is already a task for this today."
                    created = False


                    

            if created:
                data = {'status': 200, 'data': str(bill), 'newly_created': 1, 'msg': str(bill) + ' generated successfully'}
            else:
                data = {'status': 200, 'data': str(bill), 'newly_created': 0, 'msg': str(bill) + ' previously generated'}
          
            status = 200

        except Exception, e:
            print "Exception", e
            data = {'status': 200, 'data': None, 'msg': u'Unable to generate bill for account ' + 
                            unicode(account) + u' for billing schedule ' + unicode(bs) }
            status = 400

        return self.render_to_json_response(data, status=status)


@login_required
@ajax_view
class RegenerateBillView(DetailView):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        #today = business_date_to_date() #timezone.now().date()
        #bs =  BillingSchedule.objects.get(start_date__lte=today, end_date__gte=today)
        today = datetime.strptime(Config.objects.get(name='business_date').value, '%Y-%m-%d').date()
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        account = None
        try:
            bill = 'Bills'   
            if kwargs.get('pk'):
                account = self.model.objects.get(id = kwargs.get('pk'))
                bill, created = account.regenerate_bill(user=request.user.username)
            else:
                print "No account specified. Exiting.."
                created = False


                    

            if created:
                data = {'status': 200, 'data': str(bill), 'regenerated': 1, 'msg': str(bill) + ' regenerated successfully'}
            else:
                data = {'status': 200, 'data': str(bill), 'regenerated': 0, 'msg': str(bill) + ' regeneration unsuccessful'}
          
            status = 200

        except Exception, e:
            print "Exception", e
            data = {'status': 200, 'data': None, 'msg': u'Unable to regenerate bill for account ' + 
                            unicode(account) + u' for billing schedule ' + unicode(bs) }
            status = 400

        return self.render_to_json_response(data, status=status)


@login_required
@ajax_view
class GenerateBillsView(DetailView):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        #today = business_date_to_date() #timezone.now().date()
        #bs =  BillingSchedule.objects.get(start_date__lte=today, end_date__gte=today)
        today = datetime.strptime(Config.objects.get(name='business_date').value, '%Y-%m-%d').date()
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        account = None
        try:
            bill = 'Bills'   
            task_id = kwargs.get('pk')


            print "----- creating a task.."
            task, task_created = Task.objects.get_or_create(name='Generate Bills',type='bill', business_date=today)
            print "----- task created! : ", task_created
            

            counter = 0
            if task_created:
                task.task_id = task_id
                task.created_by = request.user.username
                task.save()

                print " --- generating bills "
                accounts =  self.model.objects.exclude(status='inactive') 
                total = accounts.count()
                task.jobs_total = total
                task.jobs_done = counter
                task.status = 'in progress'
                task.save()

                for account in accounts:
                    print "counter: ", counter
                    print "account: ", account
                    print "bill: ", account.bill

                    if not account.bill:
                        bill, created = account.generate_bill(business_date=str(today), period=period)
                    else:
                        print "--- bill already generated for this account: ", account

                    counter+=1
                    task.jobs_done = counter
                    task.save()

                
                print "-- finished generating bills.. "
                task.status = 'completed'                
                task.save()
                print "-- status has been saved! "


                # Create new Task for PDF generation, to be picked up by generate.py --monitor

                task2, task2_created = Task.objects.get_or_create(name='Generate Bills PDF',type='bill', business_date=today)

                if task2_created:
                    task2.status = 'pending'
                    task2.save()


            else:
                print "Cannot generate bills further, there is already a task for this today."
                created = False


                

            if created:
                data = {'status': 200, 'data': str(bill), 'newly_created': 1, 'msg': str(bill) + ' generated successfully'}
            else:
                data = {'status': 200, 'data': str(bill), 'newly_created': 0, 'msg': str(bill) + ' previously generated'}
          
            status = 200

        except Exception, e:
            print "Exception", e
            data = {'status': 200, 'data': None, 'msg': u'Unable to generate bill for account ' + 
                            unicode(account) + u' for billing schedule ' + unicode(bs) }
            status = 400

        return self.render_to_json_response(data, status=status)

