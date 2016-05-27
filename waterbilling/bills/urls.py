# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import (BillListView, 
        BillDetailView, 
        PdfBillDetailView,
        BillDatatablesView,
        FileRepoDatatablesView,
        GenerateBillView,
        RegenerateBillView,
        GenerateBillsView,
    )

urlpatterns = patterns('',
    url(r'^$', view=BillListView.as_view(template_name='bills/bill_list.html'),name='bill_list'),
    url(r'^(?P<pk>\d+)/$', view=BillDetailView.as_view(template_name='bills/bill_detail.html'),name='bill_detail'),
    url(r'^(?P<pk>\d+)/print/$', view=BillDetailView.as_view(template_name='bills/bill_detail_print.html'),name='bill_detail_print'),
    url(r'^(?P<pk>\d+)/pdf/$', view=PdfBillDetailView.as_view(template_name='bills/bill_detail_print.html'),
            name='bill_detail_pdf'),
    url(r'^datatable$', BillDatatablesView.as_view(), name='bill_list_datatable'),
    url(r'^file_datatable', FileRepoDatatablesView.as_view(), name='file_list_datatable'),
    url(r'^generatebill/$', view=GenerateBillView.as_view(),name='generate_bill'),
    url(r'^generatebill/(?P<pk>\d+)/$', view=GenerateBillView.as_view(),name='account_generate_bill'),
    url(r'^regeneratebill/(?P<pk>\d+)/$', view=RegenerateBillView.as_view(),name='account_regenerate_bill'),
    url(r'^generatebills/(?P<pk>\d+)/$', view=GenerateBillsView.as_view(),name='account_generate_bills'),
    )
