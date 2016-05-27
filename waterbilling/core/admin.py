# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models as dmodels
import models



class CoreAdmin(admin.ModelAdmin):
    readonly_fields=('created_by', 'created', 'last_updated_by', 'last_updated')
    
    exclude = ()
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.last_updated_by = request.user
        obj.save()

#http://djangosnippets.org/snippets/997/
#get the models from myproject.models]
mods = [x for x in models.__dict__.values() if issubclass(type(x), dmodels.base.ModelBase)]

admins = []
#for each model in our models module, prepare an admin class
#that will edit our model (Admin<model_name>, model) 
for c in mods: 
    admins.append(("%sAdmin"%c.__name__, c))

def list_display_creator(django_model):
    list_display = [f.name for f in django_model._meta.fields]
    return list_display

#create the admin class and register it
for (ac, c) in admins:
    try: #pass gracefully on duplicate registration errors
        print "ac", ac, "c", c
        admin.site.register(c, type(ac, (CoreAdmin,), {'list_display': list_display_creator(c)}))
    except Exception, e:
        print "error", e
        #pass

