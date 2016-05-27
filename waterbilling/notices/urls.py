# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import NoticeDetailView, PdfNoticeDetailView, GenerateNoticeView, GenerateNoticesView

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/print/$', view=NoticeDetailView.as_view(template_name='notices/notice_detail_print.html'),
    	name='notice_detail_print'),
    url(r'^(?P<pk>\d+)/pdf/$', view=PdfNoticeDetailView.as_view(template_name='notices/notice_detail_print.html'),
    		name='notice_detail_pdf'),
    url(r'^generatenotice/$', view=GenerateNoticeView.as_view(),name='generate_notice'),
    url(r'^generatenotice/(?P<pk>\d+)/$', view=GenerateNoticeView.as_view(),name='account_generate_notice'),
    url(r'^generatenotices/(?P<pk>\d+)/$', view=GenerateNoticesView.as_view(),name='account_generate_notices'),    
    )
