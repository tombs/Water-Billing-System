from .models import Config
from datetime import datetime, date
import csv, codecs, cStringIO
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission

def load_wbs_users():
    '''

    Create the default users/groups for Water Billing.

    Groups:  wbsadmin, wbsuser 
    Users:  admin, chona, ana

    '''

    # Here are the users
    chona = User.objects.create_user(username='chona', password='anohc321')
    ana = User.objects.create_user(username='ana', password='ana54321')
    chay = User.objects.create_user(username='chay', password='yahc4321')
    angie = User.objects.create_user(username='angie', password='eigna321')
    noe = User.objects.create_user(username='noe', password='eon54321')

    chris = User.objects.create_user(username='chris', password='sirhc321')
        
    wbsadmin = Group(name='wbsadmin')
    wbsadmin.save()
    wbsadmin.permissions.add(Permission.objects.get(name='Can add account'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change account'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add account meter'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change account meter'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add user'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change user'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add account type'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change account type'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add address'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change address'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add adjustment'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change adjustment'))
    #wbsadmin.permissions.add(Permission.objects.get(name='Can add bill'))
    #wbsadmin.permissions.add(Permission.objects.get(name='Can change bill'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add billing schedule'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change billing schedule'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add customer'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change customer'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add meter read'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change meter read'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add notice'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change notice'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add payment'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change payment'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add posted payment'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change posted payment'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add rate'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change rate'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can add rate charge'))
    wbsadmin.permissions.add(Permission.objects.get(name='Can change rate charge'))
    wbsadmin.save()

    wbsuser = Group(name='wbsuser')
    wbsuser.save()
    wbsuser.permissions.add(Permission.objects.get(name='Can add account meter'))
    wbsuser.permissions.add(Permission.objects.get(name='Can change account meter'))
    wbsuser.permissions.add(Permission.objects.get(name='Can add meter read'))
    wbsuser.permissions.add(Permission.objects.get(name='Can change meter read'))
    wbsuser.permissions.add(Permission.objects.get(name='Can add payment'))
    wbsuser.permissions.add(Permission.objects.get(name='Can change payment'))
    wbsuser.save()

    chona.groups.add(wbsadmin)
    chona.save()
    ana.groups.add(wbsadmin)
    ana.save()
    chay.groups.add(wbsadmin)
    chay.save()
    angie.groups.add(wbsadmin)
    angie.save()
    noe.groups.add(wbsadmin)
    noe.save()
    chris.groups.add(wbsuser)
    chris.save()

def load_wbs_configs():
    configs = settings.WATER_BILLING_CONFIG
    for key in configs:
        try:
            config = Config.objects.get(name=key).value        
        except Config.DoesNotExist:
            print "Config does not exist for: " + str(key)
            config = Config(name=key, value=configs[key])
            config.save()



def get_business_date():
	try:
		return Config.objects.get(name='business_date').value

	except Config.DoesNotExist:
		print "Warn: No config for business_date. creating a new one..."

		config = Config(
			name='business_date', 
			value=str(date.today())
		)

		config.save()

		return config.value



def business_date_to_date():

	date_str = get_business_date()

	return datetime.strptime(date_str, '%Y-%m-%d').date()


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)