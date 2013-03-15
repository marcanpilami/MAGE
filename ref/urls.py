'''
Created on 8 mars 2013

@author: Marc-Antoine
'''

from django.conf.urls import patterns, url
from ref import views

urlpatterns = patterns('',
    url(r'csv/(?P<url_end>[\d,]*)$', views.csv, name='csv'),
    url(r'envts$', views.envts, name='envts'),
    url(r'envt/(?P<envt_id>\d*)$', views.envt, name='envt'),
    url(r'types$', views.model_types, name='types'),
    url(r'mcltester$', views.mcl_tester, name='mcltester'),
)
