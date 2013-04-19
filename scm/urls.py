# coding: utf-8


from django.conf.urls import patterns, url
from scm import views

urlpatterns = patterns('',
    url(r'envts$', views.envts, name='envts'),
    url(r'delivery$', views.delivery_list, name='deliveries'),
    url(r'delivery/(?P<iset_id>\d*)$', views.delivery, name='delivery_detail'),
    url(r'delivery/edit$', views.delivery_edit, name='delivery_create'),
    url(r'delivery/(?P<iset_id>\d*)/edit$', views.delivery_edit, name='delivery_edit'),
    url(r'delivery/(?P<iset_id>\d*)/validate$', views.delivery_validate, name='delivery_validate'),
    url(r'delivery/(?P<iset_id>\d*)/editdep$', views.delivery_edit_dep, name='delivery_edit_dep'),
    url(r'delivery/test/(?P<delivery_id>\d*)/(?P<envt_id>\d*)$', views.delivery_test, name='delivery_prereqs_test'),
    url(r'delivery/applyenvt/(?P<delivery_id>\d*)/(?P<envt_id>\d*)$', views.delivery_apply_envt, name='delivery_apply_envt'),
    url(r'delivery/lcapplyenvt$', views.lc_versions_per_environment, name='lc_installs_envts'),
    url(r'demo', views.demo, name='demo'),
    url(r'envt/hist/(?P<envt_name>.*)', views.all_installs, name='envtinstallhist'),
    url(r'script/lcversions/(?P<lc_id>\d*)$', views.get_lc_versions, name='getlcversions'),         
)
