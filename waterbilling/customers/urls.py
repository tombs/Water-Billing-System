# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import (CustomerListView, CustomerDetailView, CustomerDatatablesView, CustomerAddView, CustomerUpdateView,
        )

urlpatterns = patterns('',
    url(r'^$', view=CustomerListView.as_view(template_name='customers/customer_list.html'),name='customer_list'),
    url(r'^(?P<pk>\d+)/$', view=CustomerDetailView.as_view(template_name='customers/customer_list.html'),name='customer_detail'),
    url(r'^datatable$', CustomerDatatablesView.as_view(), name='customer_list_datatable'),
    url(r'^addnewcustomer/$', view=CustomerAddView.as_view(),name='customer_add'),
    url(r'^updatecustomer/$', view=CustomerUpdateView.as_view(),name='customer_update'),
    )

