# Create your views here.
import json
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import DetailView
from .models import Account, FinancialTransaction, Notice, BillingSchedule, Config, Task
from wkhtmltopdf.views import PDFTemplateView
from core.views import login_required, ajax_view
from core.utils import get_business_date, business_date_to_date
from datetime import datetime

class NoticeDetailView(DetailView):

    model = Notice
    context_object_name = 'notice'
    
    def get_context_data(self, **kwargs):
        context = super(NoticeDetailView, self).get_context_data(**kwargs)
        context['account'] = context['notice'].account
        return context

class PdfNoticeDetailView(PDFTemplateView):

    model = Notice
    context_object_name = 'notice'

    cmd_options = settings.CMD_OPTIONS.get('NOTICE',{})

    def get_context_data(self, **kwargs):
        context = super(PdfNoticeDetailView, self).get_context_data(**kwargs)
        context['notice'] = self.model.objects.get(pk=context['pk'])
        self.object = context['notice'] 
        context['account'] = context['notice'].account
        #context['now'] = timezone.now()
        return context


@login_required
@ajax_view
class GenerateNoticeView(DetailView):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        
        today = datetime.strptime(Config.objects.get(name='business_date').value, '%Y-%m-%d').date()
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        account = None

        try:
            notice = 'Notices'
            if kwargs.get('pk'):
                account = self.model.objects.get(id = kwargs.get('pk'))
                notice, created = account.generate_notice(today)
            else:
                print "----- creating a task.."
                task, task_created = Task.objects.get_or_create(name='Generate Notices PDF',type='notice', business_date=today)
                print "----- task created! : ", task_created

                if task_created:                
                    print "--> generating multiple notices.."
                    for account in self.model.objects.filter(status='for disconnection'):
                        notice, created = account.generate_notice(business_date=today, period=period)
                
                    print "-- finished generating notices.. "
                    task.status = 'pending'
                    task.created_by = request.user.username
                    task.save()
                    print "-- status has been saved! "

                else:
                    print "Cannot generate notices further, there is already a task for this today."
                    created = False




            print "created: ", created
            print "notice: ", notice
            if created:
                data = {'status': 200, 'data': str(notice), 'msg': str(notice) + ' generated successfully'}
            else:
                data = {'status': 200, 'data': str(notice), 'msg': str(notice) + ' previously generated'}
            status = 200
     
        except Exception, e:
            print "Exception", e
            data = {'status': 200, 'data': None, 'msg': u'Unable to generate notice for account ' + 
                            unicode(account) + u' for billing schedule ' + unicode(bs) }
            status=400

        return self.render_to_json_response(data, status=status)




@login_required
@ajax_view
class GenerateNoticesView(DetailView):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        
        today = datetime.strptime(Config.objects.get(name='business_date').value, '%Y-%m-%d').date()
        period = Config.objects.get(name='active_period').value
        bs = BillingSchedule.objects.get(pk=period)
        account = None

        try:
            notice = 'Notices'

            task_id = kwargs.get('pk')

            print "----- creating a task.."
            task, task_created = Task.objects.get_or_create(name='Generate Notices',type='notice', business_date=today)
            print "----- task created! : ", task_created
            

            counter = 0
            if task_created:              
                task.task_id = task_id
       
                task.created_by = request.user.username
                task.save()  
                print " --- generating notices "
                #accounts =  self.model.objects.filter(status='for disconnection')
                accounts =  self.model.objects.all()
                total = accounts.count()
                task.jobs_total = total
                task.jobs_done = counter
                task.status = 'in progress'
                task.save()

                
                print "--> generating multiple notices.."
                for account in accounts:
                    notice, created = account.generate_notice(business_date=today, period=period)
                    counter+=1
                    task.jobs_done = counter
                    task.save()

                print "-- finished generating notices.. "
                task.status = 'completed'                
                task.save()
                print "-- status has been saved! "

                # Create new Task for PDF generation, to be picked up by generate.py --monitor

                task2, task2_created = Task.objects.get_or_create(name='Generate Notices PDF',type='notice', business_date=today)

                if task2_created:
                    task2.status = 'pending'
                    task2.save()



            else:
                print "Cannot generate notices further, there is already a task for this today."
                created = False




            print "created: ", created
            print "notice: ", notice
            if created:
                data = {'status': 200, 'data': str(notice), 'msg': str(notice) + ' generated successfully'}
            else:
                data = {'status': 200, 'data': str(notice), 'msg': str(notice) + ' previously generated'}
            status = 200
     
        except Exception, e:
            print "Exception", e
            data = {'status': 200, 'data': None, 'msg': u'Unable to generate notice for account ' + 
                            unicode(account) + u' for billing schedule ' + unicode(bs) }
            status=400

        return self.render_to_json_response(data, status=status)