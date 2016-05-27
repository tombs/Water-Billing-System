# -*- coding: utf-8 -*-
# Create your views here.
import json
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.http import HttpResponse
from django.views.generic import View, ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from eztables.views import DatatablesView
from core.views import login_required, ajax_view
from core.masterlist import WbsMasterList
from .models import Bill, BillingSchedule, Account, FileRepo
from wkhtmltopdf.views import PDFTemplateView


import os, tempfile, zipfile
from django.core.servers.basehttp import FileWrapper

@login_required
class BillListView(TemplateView):
    pass

@login_required
@ajax_view
class BillDatatablesView(DatatablesView):
    model = Bill
    fields = (
        'id',
        '{account__customer__last_name}, {account__customer__first_name}',
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
class FileDownloadView(View):
    model = FileRepo

    def get(self, request, *args, **kwargs):
        print "args: " + str(args)
        print "kwargs: " + str(kwargs)
        fl = self.model.objects.get(id=kwargs['pk'])   
        fs = FileSystemStorage()              
        filename = fl.file_name    
        print "filename: " + str(filename)
        wrapper = FileWrapper(fs.open(filename))
        response = HttpResponse(wrapper, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=' + fl.file_name + ''
        response['Content-Length'] = os.path.getsize(fs.location+'/'+filename)
        return response 
           
@login_required
class PdfBillDetailView(PDFTemplateView):

    model = Bill
    context_object_name = 'bill_detail'

    def get_context_data(self, **kwargs):
        print "kwargs: " + str(kwargs)
        context = super(PdfBillDetailView, self).get_context_data(**kwargs)
        print 
        context['bill_detail'] = self.model.objects.get(pk=context['pk'])
        self.object = context['bill_detail'] 
        context['account'] = context['bill_detail'].account
        #context['now'] = timezone.now()
        return context

@login_required
@ajax_view
class GenerateMasterlistView(View):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        today = timezone.now().date()
        bs =  BillingSchedule.objects.get(start_date__lte=today, end_date__gte=today)

   
        try:
            wbx = WbsMasterList()
            wbx.render()
            wbx.save()

            print "Done with Master List Generation"

            data = {'status': 200, 'msg': 'Done with Master List Generation'}
            status = 200
        except Exception, e:
            print "e: ", str(e)
            data = {'status': 400, 'msg': 'Unable to Generate Master List' }
            status = 400

        return self.render_to_json_response(data, status=status) 


@login_required
class GetMasterlistView(View):

    model = Account
     
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self, request, *args, **kwargs):
        print "This GET", args, kwargs
        today = timezone.now().date()
        bs =  BillingSchedule.objects.get(start_date__lte=today, end_date__gte=today)

        wbx = WbsMasterList()
        
        fs = FileSystemStorage()              
        filename = wbx.filename

        print "filename: " + str(filename)
        wrapper = FileWrapper(fs.open(filename))
        response = HttpResponse(wrapper, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=' + filename + ''
        response['Content-Length'] = os.path.getsize(fs.location+'/'+filename)
        return response

