# coding: utf-8

from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^MAGE/', include('MAGE.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root),
    (r'^gcl/install/list/(?P<envt_name>.*)', 'MAGE.gcl.views.installs_list_envt'),
    (r'^gcl/install/listc/(?P<compoID>.*)', 'MAGE.gcl.views.installs_comp'),
    (r'^gcl/tag/list$', 'MAGE.gcl.views.tag_list'),
    (r'^pa.*$', 'MAGE.pda.views.page_de_garde'),
    
    
    # This is for dev only ! static content should be served by the webserver itself
    (r'^mediamage/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'C:/Users/user1/WebDjango/MAGE/MAGE/CSS'}),

)
