# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import AdjustmentView

urlpatterns = patterns('',
    url(r'^$', view=AdjustmentView.as_view(),name='new_adjustment'),
	)