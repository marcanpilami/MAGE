# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.conf.urls import patterns, url
from ref import views

urlpatterns = patterns('',
    url(r'^envt$', views.envts, name='envts'),
    url(r'^templates$', views.templates, name='templates'),
    url(r'^envt/(?P<envt_id>\d*)$', views.envt, name='envt'),
    url(r'^envt/(?P<envt_name>.*)/duplicate$', views.envt_duplicate_name, name='envt_duplicate'),

    url(r'type$', views.model_types, name='types'),
    url(r'types_details$', views.model_detail, name='types_details'),

    ## Creation forms
    url(r'new$', views.new_items, name='new_item'),
    url(r'new/ci/(?P<description_id>\d*)$', views.new_ci_step1, name='new_item_ci'),
    url(r'ci/(?P<instance_id>\d*)$', views.new_ci_step2, name='edit_ci'),

    ## MQL
    url(r'mqltester$', views.mql_tester, name='mqltester'),
    url(r'mql/(?P<output_format>.*)/(?P<query>.*)$', views.mql_query, name='mqlquery'),

    ## Graphs
    url(r'gph/full$', views.full_pic, name='grfull'),
    url(r'gph/filter/(?P<nbRelGenerations>\d*)/(?P<collapseThr>\d*)', views.filter_pic, name='grfilter'),
    url(r'mplg$', views.view_carto, name='grmain'),
    url(r'gph/envt/(?P<envt_id>\d*)/*$', views.envt_pic, name='grenvt'),

    url(r'urls', views.urls, name='urls'),

    ## Instances
    url(r'^instance/new/(?P<description_id>\d+)$', views.edit_comp, name='instance_new'),
    url(r'^instance/(?P<instance_id>\d+)$', views.edit_comp, name='instance_edit'),
    url(r'^instance/(?P<instance_id>\d+)/(?P<description_id>\d+)$', views.edit_comp, name='instance_edit_descr'),

    url(r'^instance/envt/(?P<envt_id>\d+)$', views.envt_instances, name='instance_envt'),
)

