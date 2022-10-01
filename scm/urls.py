# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.urls import re_path, include
from django.conf import settings

from scm import views

app_name='scm'

# Interactive views & forms
urlpatterns_interactive = [
    ###########################################################################
    ## Interactive views
    ###########################################################################

    # Progression
    re_path(r'envt/(?P<envt_name>.+)/hist/(?P<limit>\d+)/', views.all_installs, name='envtinstallhistprm'),
    re_path(r'envt/(?P<envt_name>.+)/hist/', views.all_installs, {'limit': 90}, name='envtinstallhist'),

    # Delivery referential
    re_path(r'delivery/$', views.delivery_list, name='deliveries'),
    re_path(r'delivery/(?P<iset_id>\d+)$', views.delivery, name='delivery_detail'),

    # Delivery hand-off forms
    re_path(r'delivery/edit/$', views.delivery_edit, name='delivery_create'),
    re_path(r'delivery/(?P<iset_id>\d*)/edit/$', views.delivery_edit, name='delivery_edit'),
    re_path(r'delivery/(?P<iset_id>\d*)/editdep/$', views.delivery_edit_dep, name='delivery_edit_dep'),

    # Applying installable sets/items - forms
    re_path(r'is/(?P<iset_id>\d*)/testonenvtform/(?P<envt_id_or_name>.+)$', views.iset_test, name='delivery_prereqs_test'),
    re_path(r'is/(?P<iset_id>\d*)/applytoenvt/(?P<envt_id_or_name>.+)/force$', views.iset_apply_envt, {'force_prereqs' : True}, name='iset_apply_envt_force'),
    re_path(r'is/(?P<iset_id>\d*)/applytoenvt/(?P<envt_id_or_name>.+)$', views.iset_apply_envt, {'force_prereqs' : False}, name='iset_apply_envt_force'),
    re_path(r'bck/$', views.backup_list, name='backup_list'),
    re_path(r'bck/archive$', views.backup_list, {'archive': True}, name='backup_list_archive'),
    re_path(r'bck/(?P<bck_id>\d*)$', views.backup_detail, name='backup_detail'),
    
    # Backup
    re_path(r'bck/create/envtdefault/(?P<envt_name>.*)$', views.backup_envt, name='backup_envt'),
    re_path(r'bck/create/form/(?P<envt_name>.*)$', views.backup_envt_manual, name='backup_envt_manual'),
    re_path(r'bck/latest/ci/(?P<ci_id>\d*)/age$', views.latest_ci_backupset_age_mn, name='latest_ci_backupset_age_mn'),
    re_path(r'bck/latest/ci/(?P<ci_id>\d*)/id$', views.latest_ci_backupset_id, name='latest_ci_backupset_id'),

    # Retrieving current version of elements
    re_path(r'version/summary/$', views.lc_versions_per_environment, name='lc_installs_envts'),
    re_path(r'version/lc/$', views.lc_list, name='lc_list'),
    re_path(r'version/lc/(?P<lc_id>\d*)$', views.lc_versions, name='lc_versions'),

    # Tags
    re_path(r'tag/$', views.tag_list, name='tag_list'),
    re_path(r'tag/(?P<tag_id>\d*)$', views.tag_detail, name='tag_detail'),
    re_path(r'tag/create/(?P<envt_name>.*)/(?P<tag_name>.*)$', views.tag_create, name='tag_create'),
    re_path(r'tag/(?P<tag_id>.*)/remove$', views.tag_remove, name='tag_remove'),

    # IS life cycle
    re_path(r'is/(?P<iset_id>\d*)/validate$', views.iset_validate, name='iset_validate'),
    re_path(r'is/(?P<iset_id>\d*)/invalidate$', views.iset_invalidate, name='iset_invalidate'),
    re_path(r'is/(?P<is_id>\d*)/archive$', views.iset_archive, name='iset_archive'),
    re_path(r'is/(?P<is_id>\d*)/unarchive$', views.iset_unarchive, name='iset_unarchive'),
]

urlpatterns_script = [

    ###########################################################################
    ## Script APIs (using direct path without project for ascending compatibility)
    ###########################################################################

    # Applying installable sets/items
    re_path(r'is/(?P<iset_id>\d*)/testonenvtscript/(?P<envt_id_or_name>.+)$', views.iset_test_script, name='delivery_prereqs_test_script'),
    re_path(r'is/(?P<iset_id>\d*)/applytoenvt/(?P<envt_id_or_name>.+)$', views.iset_apply_envt, name='iset_apply_envt'),
    re_path(r'ii/(?P<ii_id>\d+)/apply/(?P<envt_name>.+)/(?P<instance_id>\d+)$', views.delivery_ii_apply_envt, name='delivery_apply_ii_single'),
    re_path(r'ii/(?P<ii_id>\d+)/testonenvtscriptfull/(?P<envt_name>.+)$', views.delivery_ii_test_envt, {'full_delivery': True}, name='delivery_test_ii_set'),
    re_path(r'ii/(?P<ii_id>\d+)/testonenvtscriptsingle/(?P<envt_name>.+)$', views.delivery_ii_test_envt, name='delivery_test_ii_single'),
    re_path(r'ii/(?P<ii_id>\d+)/installmethod/(?P<ci_id>\d+)$', views.ii_test_applicable_to_ci, name='ii_test_compat_ci'),

    # Retrieving current version of elements
    re_path(r'version/lc/(?P<lc_id>\d*)/json$', views.get_lc_versions, name='lc_versions_export'),
    
    # Tags
    re_path(r'tag/create/(?P<envt_name>.*)/(?P<tag_name>.*)$', views.tag_create_script, name='tag_script_create'),
    re_path(r'tag/(?P<tag_id>.*)/remove$', views.tag_remove_script, name='tag_script_remove'),
    
    # Backup
    re_path(r'bck/create/envtdefault/(?P<envt_name>.*)$', views.backup_envt, name='backup_script_envt'),
    re_path(r'bck/create/script/(?P<envt_name>.*)/(?P<ci_id>\d*)$', views.backup_script, name='backup_script_create'),
    re_path(r'bck/create/script/(?P<envt_name>.*)/(?P<ci_id>\d*)/(?P<bck_id>\d*)$', views.backup_script, name='backup_script_add'),
    re_path(r'bck/latest/envt/(?P<envt_name>.*)/id$', views.latest_envt_backupset_id, name='latest_envt_backupset_id'),

    # Queries on IS & II
    re_path(r'is/(?P<iset>.*)/export/(?P<output_format>.*)$', views.iset_export, name='iset_export'),
    re_path(r'is/(?P<iset_name>.*)/id$', views.iset_id, name='iset_id'),
    re_path(r'is/(?P<iset_id>.+)/ii/iicompatlist/(?P<ci_id>\d+)$', views.iset_get_applicable_ii, name='iset_ii_ii_compat'),
    re_path(r'ii/(?P<ii_id>\d+)/export/sh$', views.ii_export, name='ii_export'),

    # IS life cycle
    re_path(r'is/(?P<iset_id>\d*)/validate$', views.iset_validate_script, name='iset_script_validate'),
    re_path(r'is/(?P<iset_id>\d*)/invalidate$', views.iset_invalidate_script, name='iset_script_invalidate'),
    re_path(r'is/(?P<is_id>\d*)/archive$', views.iset_archive_script, name='iset_script_archive'),
    re_path(r'is/(?P<is_id>\d*)/unarchive$', views.iset_unarchive_script, name='iset_script_unarchive'),
]

urlpatterns = [
    re_path(r'^project/(?P<project_id>\d+)/', include(urlpatterns_script)),
    re_path(r'^', include((urlpatterns_script, 'scm'), namespace='default_project'), kwargs={'project_id': settings.DEFAULT_PROJECT_ID}),
    re_path(r'^project/(?P<project_id>\d+)/', include(urlpatterns_interactive)),
]
