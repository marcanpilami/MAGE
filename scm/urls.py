# coding: utf-8


from django.conf.urls import patterns, url
from scm import views

urlpatterns = patterns('',
    url(r'envts$', views.envts, name='envts'),
    url(r'delivery$', views.delivery_list, name='deliveries'),
    url(r'delivery/(?P<delivery_id>\d*)$', views.delivery, name='delivery_detail'),
    url(r'delivery/new$', views.delivery_edit, name='delivery_edit'),
    url(r'delivery/test/(?P<delivery_id>\d*)/(?P<envt_id>\d*)$', views.delivery_test, name='delivery_prereqs_test'),
    url(r'delivery/applyenvt/(?P<delivery_id>\d*)/(?P<envt_id>\d*)$', views.delivery_apply_envt, name='delivery_apply_envt'),
    url(r'demo', views.demo, name='demo'),
    url(r'envt/hist/(?P<envt_name>.*)', views.all_installs, name='envtinstallhist'),     
)
