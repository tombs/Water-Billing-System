# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import (MeterReadListView,
	MeterReadDetailView, 
	MeterReadUploadView,
	MeterReadDatatablesView,
	MeterReadDownloadFileView,
    MeterReadUpdateView,
    MeterAddView,
	)

urlpatterns = patterns('',
    url(r'^$', view=MeterReadListView.as_view(template_name='meters/meter_read_list.html'),name='meter_read_list'),
    url(r'^(?P<pk>\d+)/$', view=MeterReadDetailView.as_view(template_name='meters/meter_read_list.html'),name='meter_read_detail'),
    url(r'^uploadreading/$', view=MeterReadUploadView.as_view(),name='meter_read_upload'),
    url(r'^datatable$', MeterReadDatatablesView.as_view(), name='meterread_list_datatable'),
    url(r'^downloadtemplate/$', view=MeterReadDownloadFileView.as_view(),name='meter_read_download'),
    url(r'^updatemeterread/$', view=MeterReadUpdateView.as_view(),name='meter_read_update'),
    url(r'^addnewmeter/$', view=MeterAddView.as_view(),name='meter_add'),
    )