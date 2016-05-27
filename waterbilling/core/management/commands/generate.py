# -*- coding: utf-8 -*-
"""
dataloader.py
Facility to load data into the database

"""
import os
import csv
import sys
from datetime import date, datetime
import time
import codecs
from tempfile import NamedTemporaryFile
from StringIO import StringIO
from PyPDF2 import PdfFileMerger
from ConfigParser import ConfigParser 

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.test.client import RequestFactory
from django.utils.encoding import smart_str
from django.contrib.auth import authenticate, login
from wkhtmltopdf.utils import wkhtmltopdf, make_absolute_paths

from optparse import make_option
#import argparse

from core import models
from core.utils import get_business_date, business_date_to_date

from bills.views import PdfBillDetailView, BillDetailView
from notices.views import PdfNoticeDetailView, NoticeDetailView


class Creator(object):
    '''
    Base class for generating stuff (report, pdf, bills, notices)
    '''

    def __init__(self, type, file_prefix, business_date=None, period=None, output_dir='', ):
        self.factory = RequestFactory()
        
        # get active period from Config
        if period is None:
            period = models.Config.objects.get(name='active_period').value
 
        if business_date is None:
            business_date = models.Config.objects.get(name='business_date').value

        print "period: ", period
        print "business_date: ", business_date
        bs = models.BillingSchedule.objects.get(pk=period)
        self.billing_schedule = bs
        self.period = period
        self.reading_period = bs.reading_start_date.strftime('%b %d, %Y') + " to " + bs.reading_end_date.strftime('%b %d, %Y')


        self.business_date = business_date
        self.file_prefix = file_prefix
        self.output_dir = output_dir
        
        
        self.type = type
        if self.type == 'bill':
            self.cmd_options={'zoom': 0.7, 'orientation':'Landscape', 'page-size': 'Folio',
                 'grayscale': True, 'lowquality': True}
            self.Model = models.Bill
            self.filter_attribute = 'bill_date'
            self.url_prefix = '/bills/'
            self.pdf_view = PdfBillDetailView.as_view(template_name='bills/bill_detail_print.html',  
                cmd_options=self.cmd_options
                )
        elif self.type == 'notice':
            self.cmd_options={'zoom': 0.7, 'orientation':'Portrait', 'page-width':'108','page-height':'140',
                     'grayscale': True, 'lowquality': True}
            self.Model = models.Notice
            self.filter_attribute = 'notice_date'
            self.url_prefix = '/notices/'
            self.pdf_view = PdfNoticeDetailView.as_view(template_name='notices/notice_detail_print.html',  
                cmd_options=self.cmd_options)
        else:
            raise Exception('Unknown Creator type %s'%type)

    def create(self):
        data = []
        for account in models.Account.objects.exclude(status='inactive').all():
            if self.type == 'bill':         
                data.append(account.generate_bill(business_date=self.business_date, period=self.period))
            elif self.type == 'notice':
                data.append(account.generate_notice(business_date=self.business_date, period=self.period))

        print self.type, "data count", len(data)


    def monitor_tasks(self):
    
        import time as dtime
        if self.type == 'bill':
            name = 'Generate Bills PDF'
        else:
            name = 'Generate Notices PDF'

        while True:
            # Get current time
            time = datetime.now().time()

            # Get configured cut-off time
            cutoff = datetime.strptime(models.Config.objects.get(name='monitor_cutoff').value,'%H:%M').time()

            # Check if the time is already past the cut-off time. 
            # If yes, exit the script
            if time > cutoff:
                print "Cutoff: ", cutoff
                print "Time: ", time
                print "Exceeded cutoff time.. exiting.. "
                exit()

            print "checking for " + self.type + " task"
            task = models.Task.objects.filter(type=self.type,name=name, status='pending',business_date=self.business_date)
            print "%d tasks found!" % task.count() 
            if task.count() > 0:
                self.pdf()

            print "sleeping for 60 seconds.. "
            dtime.sleep(60)


    def pdf(self):
        """
        Create the pdf for bill and notice
        need an authentication in order to be able to render the pdf as login_required decorator is in the pdf_view
        #http://stackoverflow.com/questions/3222549/how-to-automatically-login-a-user-after-registration-in-django
        """

        print "writing", self.type, self.business_date, self.Model.objects.filter(**{self.filter_attribute:self.business_date}).count()
        merger = PdfFileMerger()

        if self.type == 'bill':
            name = 'Generate Bills PDF'
        else:
            name = 'Generate Notices PDF'
   
        task, created = models.Task.objects.get_or_create(type=self.type,name=name, status='pending',business_date=self.business_date)
    
        objects =  self.Model.objects.filter(**{self.filter_attribute:self.business_date}).order_by(*['account__address__address4','account__address__address2','account__address__address3'])

        task.jobs_total = objects.count()
        task.jobs_done = 0
        task.reading_period = self.billing_schedule.reading_start_date.strftime("%b %d, %Y") + " To " + self.billing_schedule.reading_end_date.strftime("%b %d, %Y")
        jobs_done = 0

        task.save()

        for i in objects:
            print self.type, "object", i.pk, i
            request = self.factory.get(self.url_prefix + str(i.pk) + '/pdf/')
            #login(request, admin)
            request.user = self.user
            response = self.pdf_view(request, **{'pk':i.pk})
            response.render()
            merger.append(StringIO(response.content))
            jobs_done+=1
            task.jobs_done = jobs_done
            task.status = 'in progress'
            task.save()    
	    

        output_file = u'-'.join([
                        self.file_prefix,  
                        u'ALL',
                        self.business_date.strftime(u'%Y-%m-%d')]) + u'.pdf'
        print "output_file: " + str(output_file)
        if self.Model.objects.filter(**{self.filter_attribute:self.business_date}).count()>0:
            fs = FileSystemStorage()  # Create a storage instance "fs" from where to store "myfile"            
            f = open(output_file,'wb') # open the output file as "f"
            merger.write(f)
            f.close()
            
            g = open(output_file,'rb')
            myfile = File(g)
            if fs.exists(output_file):
                print "It exists already! : ", output_file
                print "Overwriting.."
                fs.delete(output_file)
            fs.save(output_file,myfile)         
            os.remove(output_file)   
            
            from datetime import date
            filerepo, created = models.FileRepo.objects.get_or_create(file_name=output_file, generation_date=date.today(), business_date=self.business_date)

            if created:
                print "created a new file record!"
                filerepo.file_name = output_file
                filerepo.file_type = self.type
                if self.type == 'bill':
                    filerepo.file_description = "all bills"
                elif self.type == 'notice':
                    filerepo.file_description = "all notices"
                filerepo.generation_date = date.today()
                filerepo.business_date = self.business_date
                filerepo.reading_period = self.reading_period
                filerepo.save() 
            else:
                print "File already exists!: ", output_file
                filerepo.generation_date = date.today()
                filerepo.save()

            task.result = "Saved as file: ", output_file

        else:
            print "no pdf generateed for", self.file_prefix
            task.result = "no pdf generateed for", self.file_prefix

        task.status = 'completed'
        task.save()


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'
    option_list = BaseCommand.option_list + (
        make_option('--type',         
            dest='type',
            nargs=1,
            default=False,
            help='create pdf of notices or bills'),
        make_option('--business-date',
            dest="business_date", 
            nargs=1, 
            default=None,            
            help='business date to use'),
        make_option('--file-prefix',
            dest="file_prefix", 
            nargs=1, 
            default=None,            
            help='file prefix to use'),
        make_option('--output-dir',
            dest="output_dir", 
            nargs=1, 
            default='',            
            help='file prefix to use'),
        make_option('--pdf',
            action="store_true",            
            dest='pdf',
            default=False,
            help='generate pdf'),
        make_option('--create',
            action="store_true",            
            dest='create',
            default=False,
            help='create bill/notice'),
       

        make_option('--username',      
            dest='username',
            nargs=1,
            default=None,
            help='username'),
        

        make_option('--password',         
            dest='password',
            nargs=1,
            default=None,
            help='password'),

        make_option('--config',
            nargs=1,            
            dest='config',
            default=None,
            help='config file'),

        make_option('--monitor',
            action="store_true",            
            dest='monitor',
            default=False,
            help='monitor pdf generation tasks'),


        )


    def parse_config(self, config):
        conf = ConfigParser()

        try:
            conf.read(config)

            return dict(conf.items('credentials'))
        except Exception,e:
            print 'Error parsing config. ',e

            return {}


    def do_authenticate(self, credentials):
	return authenticate(username=credentials['username'], password=credentials['password'])

        
    def handle(self, *args, **options):
        print "options", options
        
        
        if options['business_date']:
            value = options.pop('business_date')
            print "business_date: ", value
            if value in ('now','today'):
                business_date = models.Config.objects.get(name='business_date').value
                business_date = datetime.strptime(business_date,'%Y-%m-%d').date()
            else:
                business_date = datetime.strptime(value,'%Y-%m-%d').date()
        else:
            business_date =  business_date_to_date() #date.today()

        if options['type']:
            type =options.pop('type')
            print 'generating', type, options

        if options['username'] and options['password']:
            user = self.do_authenticate(options)

        elif options['config']:
            user = self.do_authenticate(self.parse_config(options['config']))

        else:

            user = None

        if user: 
                
            creator = Creator(business_date=business_date, type=type, file_prefix=options['file_prefix'],output_dir=options['output_dir'])
            creator.user = user
                
            if options['create']:
               creator.create() 
            if options['pdf']:
                creator.pdf()
            if options['monitor']:
                creator.monitor_tasks()

        else:

            print """Inavalid User/Password supplied."""
            
            
