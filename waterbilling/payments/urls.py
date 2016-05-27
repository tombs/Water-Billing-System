# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import PaymentView, PaymentPostView, PaymentFailView

urlpatterns = patterns('',
    url(r'^$', view=PaymentView.as_view(),name='new_payment'),
    url(r'^post/(?P<pk>\d+)/$', view=PaymentPostView.as_view(),name='post_payment'),
    url(r'^fail/(?P<pk>\d+)/$', view=PaymentFailView.as_view(),name='fail_payment'),
	)