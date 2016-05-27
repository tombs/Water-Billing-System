"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from csv import DictReader
from os.path import dirname, join, normpath
from django.conf import settings
from django.test import TestCase
from .models import Meter, MeterRead
from core.management.commands.dataloader import RateLoader, AccountTypeLoader, RateChargeLoader, BillingScheduleLoader, FelizanaLoader

#DJANGO_ROOT = dirname(dirname(__file__))

# Absolute filesystem path to the top-level project folder:
#SITE_ROOT = dirname(DJANGO_ROOT)

#print "DJANGO_ROOT: ", DJANGO_ROOT
#print "SITE_ROOT: ", SITE_ROOT

class MeterReadUploadTestCase(TestCase):
    def setUp(self):
        #settings.DEBUG = True
        RateLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/rate.csv'))).load()
        AccountTypeLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/accounttype.csv'))).load()
        RateChargeLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/ratecharge.csv'))).load()
        BillingScheduleLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/billingschedule.csv'))).load()
        FelizanaLoader(normpath(join(settings.SITE_ROOT, 'core/fixtures/felizana_customer_info_2014-02.csv'))).load()

    def test_meter_read_upload_success(self):
        meterread_filename = normpath(join(settings.SITE_ROOT, 'core/fixtures/meterread_upload.csv'))
        #filename = "../core/fixtures/meterread_upload.csv"
        open_file = open(meterread_filename, "r")
        read_file = DictReader(open_file)
        """
        test_data = [
            {
                "meter"           : Meter.objects.get(meter_uid=49830),
                "previous_reading": 250,
                "address"         : "BLK 1 LOT 1 PHASE 1, FELIZANA ESTATE SUBD., BRGY. PASONG BUAYA, IMUS, CAVITE",
                "customer"        : "TAMBUNGALAN, JANELLE",
            },
            {
                "meter"           : Meter.objects.get(meter_uid=2218693),
                "previous_reading": 136,
                "address"         : "BLK 1 LOT 3 PHASE 1, FELIZANA ESTATE SUBD., BRGY. PASONG BUAYA, IMUS, CAVITE",
                "customer"        : "ARRIOLA, CHERYLYN",
            }
        ]
        """
        uploaded_data = []

        for row in read_file:
            meter_uid = row.pop('meter_uid')
            meter = Meter.objects.get(meter_uid=meter_uid)
            previous_reading = row.pop('previous_reading')
            address = row.pop('address')
            customer = row.pop('customer')
            row['meter'] = meter
            uploaded_data.append(MeterRead(**row))
            uploaded_data[-1].save()

        #self.assertEqual(test_data, uploaded_data)
        self.assertEqual(uploaded_data[0].meter, Meter.objects.get(meter_uid=49830))
        self.assertEqual(uploaded_data[1].meter, Meter.objects.get(meter_uid=2218693))
        #add more assertions for customer name, address, previous meter reading

"""
class MeterReadUploadView(CreateView):
    form_class = MeterReadUploadForm
    model = MeterRead

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    # def get(self, request, *args, **kwargs):
    #   print "This POST"
    #   form = self.form_class(initial=self.initial)
    #   return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        
        form = self.form_class(request.POST, request.FILES)        
        print "REQUEST", request.POST, request.FILES, request.is_ajax()
        print "FORM", form.is_valid(), form.errors
        if form.is_valid():
            reader= csv.DictReader(form.cleaned_data["file"])

            data = []
            errors = []
            for row in reader:

                try:
                    meter_uid = row.pop('meter_uid')
                    meter = Meter.objects.get(meter_uid=meter_uid)
                    previous_reading = row.pop('previous_reading')
                    address = row.pop('address')
                    customer = row.pop('customer')
                    row['meter'] = meter
                    data.append(self.model(**row))
                    data[-1].save()                    
                except Exception, e:
                    print "Skipping row with Error", meter_uid, customer, address, row, e
                    errors.append({'meter_uid': meter_uid, 'address': address, 
                            'customer': customer, 'previous_reading': previous_reading,
                            'exception': unicode(e)}
                            )
                    continue


            #     form = MeterReadForm(**row)
            #     print "row, cleaned", form.cleaned_data         
            #     if form.is_valid():
            #         # we don't want to put the object to the database on this step
            #         #self.instance = form.save(commit=False)
            #         data.append(form)  
            #     else:
            #         # You can use more specific error message here
            #         raise forms.ValidationError(u"The file contains invalid data.")

            #MeterRead.objects.bulk_create(data)

            if self.request.is_ajax():
                data = {
                    'data': {'count': len(data)},
                    'errors': errors
                }
                print "response data", data
                if errors:
                    return self.render_to_json_response(data, status=409) #conflict
                else:
                    data['message'] = 'succesful'
                    return self.render_to_json_response(data)

            return HttpResponseRedirect('/meters/')

        else:
            if self.request.is_ajax():
                result =  self.render_to_json_response(form.errors, status=400)
                print 'RESULT ', result
                return result
            return HttpResponseRedirect('/meters/')
"""