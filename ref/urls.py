'''
Created on 8 mars 2013

@author: Marc-Antoine
'''

from django.conf.urls import patterns, url
from ref import views

urlpatterns = patterns('',
    url(r'csv/(?P<titles>\d)/(?P<mcl>.*)/extract\.csv$', views.mcl_query, name='mcl_csv'),
    url(r'csv/(?P<url_end>[\d,]*)$', views.csv, name='csv'),
    
    url(r'envt$', views.envts, name='envts'),
    url(r'templates$', views.templates, name='templates'),
    url(r'envt/(?P<envt_id>\d*)$', views.envt, name='envt'),
    url(r'envt/(?P<envt_name>.*)/duplicate$', views.envt_duplicate_name, name='envt_duplicate'),
    
    url(r'type$', views.model_types, name='types'),
    url(r'types_details$', views.model_detail, name='types_details'),
    
    url(r'mcltester$', views.mcl_tester, name='mcltester'),
    url(r'mcl/get_or_create_nocv/(?P<mcl>.*)/mcl\.csv$', views.mcl_create_without_convention, name='mcl_create_nocv'),
    url(r'mcl/get_or_create_cv/(?P<mcl>.*)/mcl\.csv$', views.mcl_create, name='mcl_create_cv'),
    url(r'mcl/(?P<mcl>.*)/mcl\.csv$', views.mcl_query, name='mcl_query'),
    
    url(r'urls', views.urls, name='urls'),
)

