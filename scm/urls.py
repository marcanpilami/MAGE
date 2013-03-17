# coding: utf-8


from django.conf.urls import patterns, url
from scm import views

urlpatterns = patterns('',
    url(r'envts$', views.envts, name='envts'),
    url(r'demo', views.demo, name='demo'),
    url(r'envt/hist/(?P<envt_name>.*)', views.all_installs, name='envtinstallhist'),     
)
