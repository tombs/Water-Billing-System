# -*- coding: utf-8 -*-
# forms.py
import csv
from decimal import Decimal
from django import forms
from .models import MeterRead

class MeterReadForm(forms.ModelForm):
    
    class Meta:
        model = MeterRead
        fields = ['read_date', 'current_reading']

        # meter_id,read_date,read_time,current_reading,previous_reading,usage
        # 1,2013-01-15,00:00:00,0,0,0
        # 1,2013-02-11,00:00:00,12,0,12
        # 2,2013-01-15,00:00:00,0,0,0
        # 2,2013-02-11,00:00:00,510,0,510


    def __init__(self, *args, **kwargs):
        # Call the original __init__ method before assigning
        #    field overloads
        print args, kwargs
        self.fields['read_date'].required = True
        self.fields['current_reading'].required = True
        
        super(MeterReadForm, self).__init__(*args,
                            **kwargs)
        self.fields['previous_reading'].required = True
        self.fields['usage'].required = False
        print "self.fields", self.fields.keys()

class MeterReadUploadForm(forms.Form):
    #http://stackoverflow.com/questions/6091965/django-upload-a-file-and-read-its-content-to-populate-a-model
    file = forms.FileField()

