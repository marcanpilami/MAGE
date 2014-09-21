# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.conf.urls import patterns, url
from scm import views

urlpatterns = patterns('',
    url(r'envts$', views.envts, name='envts'),
    url(r'envt/hist/(?P<envt_name>.*)/(?P<limit>\d+)', views.all_installs, name='envtinstallhistprm'),
    url(r'envt/hist/(?P<envt_name>.*)', views.all_installs, {'limit': 31}, name='envtinstallhist'),

    url(r'delivery$', views.delivery_list, name='deliveries'),
    url(r'delivery/(?P<iset_id>\d*)$', views.delivery, name='delivery_detail'),

    # Delivery hand-off forms
    url(r'delivery/edit$', views.delivery_edit, name='delivery_create'),
    url(r'delivery/(?P<iset_id>\d*)/edit$', views.delivery_edit, name='delivery_edit'),
    url(r'delivery/(?P<iset_id>\d*)/editdep$', views.delivery_edit_dep, name='delivery_edit_dep'),

    # Applying installable sets/items
    url(r'is/(?P<iset_id>\d*)/testonenvtform/(?P<envt_id_or_name>.+)$', views.iset_test, name='delivery_prereqs_test'),
    url(r'is/(?P<iset_id>\d*)/testonenvtscript/(?P<envt_id_or_name>.+)$', views.iset_test_script, name='delivery_prereqs_test_script'),
    url(r'is/(?P<iset_id>\d*)/applytoenvt/(?P<envt_id_or_name>.+)/force$', views.iset_apply_envt, {'force_prereqs' : True}, name='iset_apply_envt_force'),
    url(r'is/(?P<iset_id>\d*)/applytoenvt/(?P<envt_id_or_name>.+)$', views.iset_apply_envt, name='iset_apply_envt'),
    url(r'ii/(?P<ii_id>\d+)/apply/(?P<envt_name>.+)/(?P<instance_id>\d+)$', views.delivery_ii_apply_envt, name='delivery_apply_ii_single'),
    url(r'ii/(?P<ii_id>\d+)/testonenvtscriptfull/(?P<envt_name>.+)$', views.delivery_ii_test_envt, {'full_delivery': True}, name='delivery_test_ii_set'),
    url(r'ii/(?P<ii_id>\d+)/testonenvtscriptsingle/(?P<envt_name>.+)$', views.delivery_ii_test_envt, name='delivery_test_ii_single'),

    # Retrieving current version of elements
    url(r'version/summary$', views.lc_versions_per_environment, name='lc_installs_envts'),
    url(r'version/lc$', views.lc_list, name='lc_list'),
    url(r'version/lc/(?P<lc_id>\d*)/json$', views.get_lc_versions, name='lc_versions_export'),
    url(r'version/lc/(?P<lc_id>\d*)$', views.lc_versions, name='lc_versions'),

    # Tags
    url(r'tag/create/(?P<envt_name>.*)/(?P<tag_name>.*)$', views.tag_create, name='tag_create'),
    url(r'tag/(?P<tag_id>.*)/remove$', views.tag_remove, name='tag_remove'),
    url(r'tag/(?P<tag_id>\d*)$', views.tag_detail, name='tag_detail'),
    url(r'tag$', views.tag_list, name='tag_list'),

    # Backup specific
    url(r'bck/create/envtdefault/(?P<envt_name>.*)$', views.backup_envt, name='backup_envt'),
    url(r'bck/create/form/(?P<envt_name>.*)$', views.backup_envt_manual, name='backup_envt_manual'),
    url(r'bck/create/script/(?P<envt_name>.*)/(?P<ci_id>\d*)$', views.backup_script, name='backup_script_create'),
    url(r'bck/create/script/(?P<envt_name>.*)/(?P<ci_id>\d*)/(?P<bck_id>\d*)$', views.backup_script, name='backup_script_add'),

    url(r'bck/latest/ci/(?P<ci_id>\d*)/age$', views.latest_ci_backupset_age_mn, name='latest_ci_backupset_age_mn'),
    url(r'bck/latest/ci/(?P<ci_id>\d*)/id$', views.latest_ci_backupset_id, name='latest_ci_backupset_id'),
    url(r'bck/latest/envt/(?P<envt_name>.*)/id$', views.latest_envt_backupset_id, name='latest_envt_backupset_id'),

    url(r'bck$', views.backup_list, name='backup_list'),
    url(r'bck/archive$', views.backup_list, {'archive': True}, name='backup_list_archive'),
    url(r'bck/(?P<bck_id>\d*)$', views.backup_detail, name='backup_detail'),

    # Queries on IS
    url(r'is/(?P<iset>.*)/export/(?P<output_format>.*)$', views.iset_export, name='iset_export'),
    url(r'is/(?P<iset_name>.*)/id$', views.iset_id, name='iset_id'),

    # IS life cycle
    url(r'is/(?P<iset_id>\d*)/validate$', views.iset_validate, name='iset_validate'),
    url(r'is/(?P<iset_id>\d*)/invalidate$', views.iset_invalidate, name='iset_invalidate'),
    url(r'is/(?P<is_id>\d*)/archive$', views.iset_archive, name='iset_archive'),
    url(r'is/(?P<is_id>\d*)/unarchive$', views.iset_unarchive, name='iset_unarchive'),
)
