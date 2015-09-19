# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.conf.urls import patterns, url
from ref import views
from ref.views.misc import project_home

urlpatterns = patterns('',
    url(r'node/(?P<folder_id>\d+)/acl', views.set_acl, name='set_acl'),
    url(r'node/(?P<project_id>\d+)$', project_home, name='project_home'),

    url(r'^envt/shared$', views.shared_ci, name='shared_ci'),
    url(r'^envt/(?P<envt_id>\d*)$', views.envt, name='envt'),
    url(r'^envt/(?P<envt_name>.*)/duplicate$', views.envt_duplicate_name, name='envt_duplicate'),

    url(r'type$', views.model_types, name='types'),
    url(r'types_details$', views.model_detail, name='types_details'),

    ## CI creation and edit forms
    url(r'new$', views.new_items, name='new_item'),
    url(r'new/ci/(?P<description_id>\d*)$', views.new_ci_step1, name='new_item_ci'),
    url(r'ci/(?P<instance_id>\d*)$', views.new_ci_step2, name='edit_ci'),
    url(r'^instance/envt/(?P<envt_id>\d+)$', views.envt_instances, name='instance_envt'),

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
    url(r'ci/backuped', views.backuped, name='backuped'),
    url(r'clearcache', views.clear_cache, name='clear_cache'),

    ## Referential debug/migration
    url(r'^debug$', views.debug, name='debug'),
    url(r'^instance/debug/all$', views.edit_all_comps_meta, name='instance_all'),
    url(r'^instance/debug/descr/(?P<descr_id>\d+)$', views.descr_instances_reinit, name='instance_descr_reinit'),
    url(r'^control$', views.control, name='control'),

    ## Script helpers
    url(r'^helpers/lib/bash$', views.shelllib_bash, name='helper_bash')
)

