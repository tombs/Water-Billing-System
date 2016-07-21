from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from core.views import DashboardView


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', DashboardView.as_view(template_name='base.html')),
    url(r'^core/', include('core.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^customers/', include('customers.urls')),
    url(r'^payments/', include('payments.urls')),
    url(r'^bills/', include('bills.urls')),
    url(r'^tasks/', include('tasks.urls')),
    url(r'^files/', include('files.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^meters/', include('meters.urls')),
    url(r'^adjustments/', include('adjustments.urls')),
    url(r'^notices/', include('notices.urls')),
    url(r'^djangojs/', include('djangojs.urls')),
    url(r'^login/', 'django.contrib.auth.views.login', {'template_name':'login.html'}),
    url(r'^logout/', 'django.contrib.auth.views.logout', {'template_name':'login.html'}),
    # Examples:
    # url(r'^$', 'waterbilling.views.home', name='home'),
    # url(r'^waterbilling/', include('waterbilling.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
