# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import (
        FileDownloadView,
        GenerateMasterlistView,
        GetMasterlistView,
    )

urlpatterns = patterns('',
    #url(r'^$', view=BillListView.as_view(template_name='bills/bill_list.html'),name='bill_list'),
    url(r'^(?P<pk>\d+)/$', view=FileDownloadView.as_view()),
    url(r'^generatemasterlist/$', view=GenerateMasterlistView.as_view()),
    url(r'^getmasterlist/$', view=GetMasterlistView.as_view()),
        )