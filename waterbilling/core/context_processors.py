from .models import Config

def business_date(request):
    try:
    	return {'BUSINESS_DATE': Config.objects.get(name='business_date').value}
    except Config.DoesNotExist:
        return {'BUSINESS_DATE': None}