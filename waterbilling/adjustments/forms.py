# -*- coding: utf-8 -*-
# forms.py
from decimal import Decimal
from django import forms
from .models import Adjustment

class AdjustmentForm(forms.ModelForm):
	

	class Meta:
		model = Adjustment
		fields = ['account', 'amount', 'description', 'adjustment_date', 'type']

	def __init__(self, *args, **kwargs):
	    # Call the original __init__ method before assigning
	    #    field overloads
	    super(AdjustmentForm, self).__init__(*args,
	                        **kwargs)
	    self.fields['amount'].required = True
	    self.fields['description'].required = True
	    self.fields['account'].widget = forms.HiddenInput()
	    self.fields['account'].required = True
	    self.fields['type'].required = True
	    adjustment_type_choices =  [('','---'),
	    							('debit','Debit (Add to Payable Balance)'),
	    							('credit','Credit (Subtract from Payable Balance)'),
	    							('reconnection_fee','Reconnection Fee (Add to Payable Balance)'),
	    							]
	    self.fields['type'] = forms.ChoiceField(choices=adjustment_type_choices)