# coding: utf-8


from django.conf.urls import patterns, url
from scm import views

urlpatterns = patterns('',
    url(r'envts$', views.envts, name='envts'),
    url(r'envt/hist/(?P<envt_name>.*)', views.all_installs, name='envtinstallhist'),
    
    url(r'delivery$', views.delivery_list, name='deliveries'),
    url(r'delivery/(?P<iset_id>\d*)$', views.delivery, name='delivery_detail'),
    
    url(r'delivery/edit$', views.delivery_edit, name='delivery_create'),
    url(r'delivery/(?P<iset_id>\d*)/edit$', views.delivery_edit, name='delivery_edit'),
    url(r'delivery/(?P<iset_id>\d*)/validate$', views.delivery_validate, name='delivery_validate'),
    url(r'delivery/(?P<iset_id>\d*)/editdep$', views.delivery_edit_dep, name='delivery_edit_dep'),
    
    url(r'delivery/(?P<delivery_id>\d*)/testonenvt/(?P<envt_id_or_name>.+)$', views.delivery_test, name='delivery_prereqs_test'),
    url(r'delivery/(?P<delivery_id>\d*)/testonenvtscript/(?P<envt_id_or_name>.+)$', views.delivery_test_script, name='delivery_prereqs_test_script'),
    url(r'delivery/(?P<delivery_id>\d*)/applytoenvt/(?P<envt_id_or_name>.+)$', views.delivery_apply_envt, name='delivery_apply_envt'),
    url(r'ii/(?P<ii_id>\d+)/apply/(?P<envt_name>.+)/(?P<instance_id>\d+)$', views.delivery_ii_apply_envt, name='delivery_apply_ii_single'),
    
    url(r'delivery/lcapplyenvt$', views.lc_versions_per_environment, name='lc_installs_envts'),
    url(r'delivery/lc$', views.lc_list, name='lc_list'),
    url(r'delivery/lc/(?P<lc_id>\d*)/versions$', views.lc_versions, name='lc_versions'),
    
    url(r'delivery/get/content/(?P<iset>.*)/csv.csv$', views.iset_content_csv, name='delivery_content_csv'),
    url(r'delivery/get/content/(?P<isetid>.*)/ksh$', views.iset_content_shell, name='delivery_content_shell'),
    url(r'delivery/get/id/(?P<iset_name>.*)$', views.iset_id, name='iset_id'),
    
    url(r'tag/create/(?P<envt_name>.*)/(?P<tag_name>.*)$', views.tag_create, name='tag_create'),
    url(r'tag/(?P<tag_id>\d*)$', views.tag_detail, name='tag_detail'),
    url(r'tag$', views.tag_list, name='tag_list'),
    
    url(r'bck/create/envtdefault/(?P<envt_name>.*)$', views.backup_envt, name='backup_envt'),
    url(r'bck/create/envtmanual/(?P<envt_name>.*)$', views.backup_envt_manual, name='backup_envt_manual'),
    url(r'bck/(?P<bck_id>\d*)$', views.backup_detail, name='backup_detail'),
    url(r'bck/(?P<is_id>\d*)/archive$', views.is_archive, name='backup_archive'),
    url(r'bck/(?P<is_id>\d*)/unarchive$', views.is_unarchive, name='backup_unarchive'),
    url(r'bck/archive$', views.backup_list_archive, name='backup_list_archive'),
    url(r'bck$', views.backup_list, name='backup_list'),
    
    url(r'demointernal', views.demo_internal, name='demointernal'),
    url(r'demo', views.demo, name='demo'),
    
    url(r'script/lcversions/(?P<lc_id>\d*)$', views.get_lc_versions, name='getlcversions'),         
)
