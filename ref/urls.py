'''
Created on 8 mars 2013

@author: Marc-Antoine
'''

from django.conf.urls import patterns, url
from ref import views

urlpatterns = patterns('',
    url(r'csv/(?P<titles>\d)/(?P<mcl>.*)/extract\.csv$', views.mcl_request, name='mcl_csv'),
    url(r'csv/(?P<url_end>[\d,]*)$', views.csv, name='csv'),
    url(r'envts$', views.envts, name='envts'),
    url(r'envt/(?P<envt_id>\d*)$', views.envt, name='envt'),
    url(r'types$', views.model_types, name='types'),
    url(r'mcltester$', views.mcl_tester, name='mcltester'),
    url(r'create/(?P<instance_type>[a-z]*)/(?P<name>[a-zA-Z0-9_ ]*)/$', views.create_instance, name='create_instance'),
)
