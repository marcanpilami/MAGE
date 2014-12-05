# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.conf.urls import patterns, url
from ref import views

urlpatterns = patterns('',
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
    url(r'gph/full$', views.carto_full, name='grfull'),
    url(r'gph/marsupilamographe$', views.carto_form, name='cartoform'),
    url(r'gph/mplgdata$', views.carto_content_form, name='cartoformdata'),
    url(r'gph/mplgdatafull/(?P<collapse_threshold>\d+)$', views.carto_content_full, name='cartofulldata'),
    url(r'gph/mplgdatasimple/(?P<ci_id_list>[\d,]+)/(?P<collapse_threshold>\d+)/(?P<select_related>\d+)$', views.carto_content, name='cartosimpledata'),
    url(r'gph/mplgdatadebug$', views.carto_debug, name='cartodebugdata'),
    url(r'gph/structuredata$', views.carto_description_content, name='cartostructuredata'),
    url(r'gph/structure$', views.carto_description, name='cartostructure'),

    ## Misc
    url(r'urls', views.urls, name='urls'),

    ## Instances
    url(r'^instance/new/(?P<description_id>\d+)$', views.edit_comp, name='instance_new'),
    url(r'^instance/(?P<instance_id>\d+)$', views.edit_comp, name='instance_edit'),
    url(r'^instance/(?P<instance_id>\d+)/(?P<description_id>\d+)$', views.edit_comp, name='instance_edit_descr'),

    url(r'^instance/envt/(?P<envt_id>\d+)$', views.envt_instances, name='instance_envt'),

    ## Script helpers
    url(r'^helpers/lib/bash$', views.shelllib_bash, name='helper_bash')
)

