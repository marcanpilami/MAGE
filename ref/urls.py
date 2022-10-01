# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.urls import include, path, re_path
from ref import views

app_name='ref'

urlpatterns_project = [
    ###########################################################################
    ## Interactive views
    ###########################################################################

    # Welcome pages
    re_path(r'^$', views.misc.project, name='project'),

    # Environment referential consultation
    re_path(r'^envt/shared/$', views.shared_ci, name='shared_ci'),
    re_path(r'^envt/(?P<envt_id>\d+)$', views.envt, name='envt'),
    re_path(r'^envt/(?P<envt_name>.*)/duplicate$', views.envt_duplicate_name, name='envt_duplicate'),

    # Meta descriptions consultation (modification is inside admin)
    re_path(r'type/$', views.model_types, name='types'),
    re_path(r'types_details/$', views.model_detail, name='types_details'),

    ## CI creation and edit forms
    re_path(r'ci/new/$', views.new_items, name='new_item'),
    re_path(r'ci/new/(?P<description_id>\d*)$', views.new_ci_step1, name='new_item_ci'),
    re_path(r'ci/(?P<instance_id>\d*)$', views.new_ci_step2, name='edit_ci'),
    re_path(r'^instance/envt/(?P<envt_id>\d+)$', views.envt_instances, name='instance_envt'),

    ## Graphs
    re_path(r'gph/full/$', views.carto_full, name='grfull'),
    re_path(r'gph/marsupilamographe/$', views.carto_form, name='cartoform'),
    re_path(r'gph/mplgdata/$', views.carto_content_form, name='cartoformdata'),
    re_path(r'gph/mplgdatafull/(?P<collapse_threshold>\d+)/$', views.carto_content_full, name='cartofulldata'),
    re_path(r'gph/mplgdatasimple/(?P<ci_id_list>[\d,]*)/(?P<collapse_threshold>\d+)/(?P<select_related>\d+)$', views.carto_content, name='cartosimpledata'),
    re_path(r'gph/mplgdatadebug$', views.carto_debug, name='cartodebugdata'),
    re_path(r'gph/structuredata/$', views.carto_description_content, name='cartostructuredata'),
    re_path(r'gph/structure/$', views.carto_description, name='cartostructure'),

    ## Misc
    re_path(r'ci/backuped/$', views.backuped, name='backuped'),

    ## Referential debug/migration
    re_path(r'^debug$', views.debug, name='debug'),
    re_path(r'^instance/debug/all$', views.edit_all_comps_meta, name='instance_all'),
    re_path(r'^instance/debug/descr/(?P<descr_id>\d+)$', views.descr_instances_reinit, name='instance_descr_reinit'),
    re_path(r'^control$', views.control, name='control'),
]

urlpatterns_nonproject = [
    ## Misc (pages)
    re_path(r'urls/$', views.urls, name='urls'),
    re_path(r'clearcache', views.clear_cache, name='clear_cache'),

    ## Script helpers (bash script download)
    re_path(r'^helpers/lib/bash$', views.shelllib_bash, name='helper_bash'),


    ###########################################################################
    ## Script APIs
    ###########################################################################

    ## MQL (scripting API)
    re_path(r'mqltester/$', views.mql_tester, name='mqltester'),
    re_path(r'mql/(?P<output_format>.*)/(?P<query>.*)$', views.mql_query, name='mqlquery'),
]

urlpatterns = [
    re_path(r'^project/(?P<project_id>[\w\-_]+)/', include(urlpatterns_project)),
    path('', include(urlpatterns_nonproject)),
]
