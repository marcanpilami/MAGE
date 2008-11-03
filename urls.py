# coding: utf-8

from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Admin
    url(r'admin/(.*)', admin.site.root, name='admin-site'),
    
    # GCL
    (r'gcl/install/list/(?P<envt_name>.*)', 'MAGE.gcl.views.installs_list_envt'),
    (r'gcl/install/listc/(?P<compoID>\d*)', 'MAGE.gcl.views.installs_comp'),
    (r'gcl/tag/list$',                      'MAGE.gcl.views.tag_list'),
    (r'gcl/ctv/list$',                      'MAGE.gcl.views.version_list'),
    (r'gcl/liv/list$',                      'MAGE.gcl.views.delivery_list'),
    
    # SAV
    (r'sav/list$',      'MAGE.sav.views.list_sav'),
    (r'sav/del$',       'MAGE.sav.views.del_sav'),
    
    # Graph app
    (r'ref/graph/full$',                                                                'MAGE.gph.views.full_pic'),
    (r'ref/graph/filter/(?P<nbParents>\d*)/(?P<nbPartners>\d*)/(?P<collapseThr>\d*).*', 'MAGE.gph.views.filter_pic'),
    (r'ref/graph$',                                                                     'MAGE.gph.views.view_carto'),
    (r'gph/envt/(?P<envt_id>\d*)/*$',                                                   'MAGE.gph.views.envt_pic'),
    
    # Default : main public pages
    (r'listepages$',    'MAGE.pda.views.liste_pages'),
    (r'pa$',            'MAGE.pda.views.page_de_garde'),
    (r'/$',             'MAGE.pda.views.page_de_garde'),
    
    # This is for dev only ! static content should be served by the webserver itself (IIS will superseed this anyway)
    (r'^mediamage/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media'}),

)
