# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'install/list/(?P<envt_name>.*)', 'MAGE.gcl.views.installs_list_envt'),
    (r'install/listc/(?P<compoID>\d*)', 'MAGE.gcl.views.installs_comp'),
    (r'tag/list$',                      'MAGE.gcl.views.tag_list'),
    (r'ctv/list$',                      'MAGE.gcl.views.version_list'),
    (r'liv/list$',                      'MAGE.gcl.views.delivery_list'),
    (r'tag/envt2tag$',                  'MAGE.gcl.views.go_to_tag_is_list'),
    (r'tag/envt2tag/(?P<envt_id>\d*)/(?P<tag_id>\d*).*', 'MAGE.gcl.views.go_to_tag_is_list'),

)