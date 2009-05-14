# coding: utf-8

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import imp

admin.autodiscover()

## note : here, there shouldn't be any urls for component applications
urlpatterns = patterns('',
    # Admin
    url(r'admin/(.*)', admin.site.root, name='admin-site'),
    
    # Auth
    (r'accounts/login/$', 'django.contrib.auth.views.login'),

    # Ref
    (r'ref/csv/(.*)', 'MAGE.ref.views.marsu'),
    
    # Default : main public pages
    (r'listepages$',    'MAGE.pda.views.liste_pages'),
    (r'pa$',            'MAGE.pda.views.page_de_garde'),
    (r'/$',             'MAGE.pda.views.page_de_garde'),
    
    # This is for dev only ! static content should be served by the webserver itself (IIS will superseed this anyway)
    (r'^mediamage/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media'}),
)

## Load applications' specific URLs
for app in settings.INSTALLED_APPS:
    if not app.split('.')[0] == 'MAGE':
        continue
    try:
        app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
    except AttributeError:
        continue
    try:
        imp.find_module('urls', app_path) #TODO: find something less memory consuming to find the module
    except ImportError:
        continue  
    urlpatterns += patterns('', (r'' + app.split('.')[1] + r'/', include(app + '.urls')) )
    
