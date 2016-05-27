# -*- coding: utf-8 -*-
# forms.py
from decimal import Decimal
from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    

    class Meta:
        model = Payment
        fields = ['account', 'amount', 'remarks', 'payment_date', 'type', 'status', 'check_number']

    def __init__(self, *args, **kwargs):
        # Call the original __init__ method before assigning
        #    field overloads
        super(PaymentForm, self).__init__(*args,
                            **kwargs)

        payment_type_choices = [('cash','Cash'),('check','Check')]
        self.fields['type'] = forms.ChoiceField(choices=payment_type_choices)
        self.fields['check_number'] = forms.CharField(required=False)
        payment_status_choices = [('new','New'),('posted','Posted'),('failed','Failed')]
        #self.fields['status'] = forms.ChoiceField(choices=payment_status_choices, initial='New')

        self.fields['amount'].required = True
        self.fields['remarks'].required = True
        self.fields['account'].widget = forms.HiddenInput()
        self.fields['account'].required = True
        self.fields['payment_date'].required = True
        self.fields['type'].required = True


    def clean(self):
        super(PaymentForm, self).clean()
        payment_type = self.cleaned_data.get("type")
        
        check_number = self.cleaned_data.get("check_number")
        if payment_type == 'check' and not check_number:
            self._errors['check_number'] = self.error_class([u'This Field is Required for Check Payment'])

        return self.cleaned_data

