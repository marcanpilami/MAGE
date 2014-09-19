# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.conf.urls import patterns, url
import ref.views.display
import ref.views.duplicate
import ref.views.edit
import ref.views.gph
import ref.views.mql
import ref.views.misc

urlpatterns = patterns('',
    url(r'^envt$', ref.views.display.envts, name='envts'),
    url(r'^templates$', ref.views.display.templates, name='templates'),
    url(r'^envt/(?P<envt_id>\d*)$', ref.views.display.envt, name='envt'),
    url(r'^envt/(?P<envt_name>.*)/duplicate$', ref.views.duplicate.envt_duplicate_name, name='envt_duplicate'),

    url(r'type$', ref.views.misc.model_types, name='types'),
    url(r'types_details$', ref.views.misc.model_detail, name='types_details'),

    ## MQL
    url(r'mqltester$', ref.views.mql.mql_tester, name='mqltester'),
    url(r'mql/(?P<output_format>.*)/(?P<query>.*)$', ref.views.mql.mql_query, name='mqlquery'),
    
    ## Graphs
    url(r'gph/full$', ref.views.gph.full_pic, name='grfull'),
    url(r'gph/filter/(?P<nbRelGenerations>\d*)/(?P<collapseThr>\d*)', ref.views.gph.filter_pic, name='grfilter'),
    url(r'mplg$', ref.views.gph.view_carto, name='grmain'),
    url(r'gph/envt/(?P<envt_id>\d*)/*$', ref.views.gph.envt_pic, name='grenvt'),

    url(r'urls', ref.views.misc.urls, name='urls'),

    ## Instances
    url(r'^instance/new/(?P<description_id>\d+)$', ref.views.edit.edit_comp, name='instance_new'),
    url(r'^instance/(?P<instance_id>\d+)$', ref.views.edit.edit_comp, name='instance_edit'),
    url(r'^instance/(?P<instance_id>\d+)/(?P<description_id>\d+)$', ref.views.edit.edit_comp, name='instance_edit_descr'),

    url(r'^instance/envt$', ref.views.edit.envt_instances, name='instance_envt'),
)

