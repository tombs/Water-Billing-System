# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import (TaskListView, TaskDatatablesView, TaskProgressView
    )

urlpatterns = patterns('',
    url(r'^$', view=TaskListView.as_view(template_name='tasks/task_list.html'),name='task_list'),
    url(r'^(?P<pk>\d+)/$', view=TaskProgressView.as_view(),name='task_progress'),
    url(r'^task_datatable', TaskDatatablesView.as_view(), name='task_list_datatable'),
      )
