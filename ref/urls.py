# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.conf.urls import patterns, url
from ref import views

urlpatterns = patterns('',
    url(r'csv/(?P<titles>\d)/(?P<mcl>.*)/extract\.csv$', views.mcl_query, name='mcl_csv'),
    url(r'csv/(?P<url_end>[\d,]*)$', views.csv, name='csv'),
    
    url(r'^envt$', views.envts, name='envts'),
    url(r'^templates$', views.templates, name='templates'),
    url(r'^envt/(?P<envt_id>\d*)$', views.envt, name='envt'),
    url(r'^envt/(?P<envt_name>.*)/duplicate$', views.envt_duplicate_name, name='envt_duplicate'),
    
    url(r'type$', views.model_types, name='types'),
    url(r'types_details$', views.model_detail, name='types_details'),
    
    ## MCL
    url(r'mcltester$', views.mcl_tester, name='mcltester'),
    url(r'mcl/get_or_create_nocv/(?P<mcl>.*)/mcl\.csv$', views.mcl_create_without_convention, name='mcl_create_nocv'),
    url(r'mcl/get_or_create_cv/(?P<mcl>.*)/mcl\.csv$', views.mcl_create, name='mcl_create_cv'),
    url(r'mcl/(?P<mcl>.*)/mcl\.csv$', views.mcl_query, name='mcl_query'),
    url(r'mcl/(?P<mcl>.*)/mcl/ksh$', views.mcl_query_shell, name='mcl_shell'),
    
    ## Graphs
    url(r'gph/full$',                                                               views.full_pic,    name='grfull'),
    url(r'gph/filter/(?P<nbRelGenerations>\d*)/(?P<collapseThr>\d*)',               views.filter_pic,  name='grfilter'),
    url(r'mplg$',                                                                   views.view_carto,  name='grmain'),
    url(r'gph/envt/(?P<envt_id>\d*)/*$',                                            views.envt_pic,    name='grenvt'),
    
    url(r'urls', views.urls, name='urls'),
    
    ## Instances
    url(r'^instance/new/(?P<description_id>\d+)$', views.edit_comp, name='instance_new'),
    url(r'^instance/(?P<instance_id>\d+)$', views.edit_comp, name='instance_edit'),
    url(r'^instance/(?P<instance_id>\d+)/(?P<description_id>\d+)$', views.edit_comp, name='instance_edit_descr'),
    
    url(r'^instance/envt$', views.envt_instances, name='instance_envt'),
)

