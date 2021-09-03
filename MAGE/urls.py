# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.urls import include, path
from django.conf.urls import url
from django.contrib.admin import autodiscover
from django.contrib.auth import views as auth_views
from ref.admin import site
from django.conf import settings
autodiscover()
from ref.views.misc import projects
from ref import views as ref_views

urlpatterns = [
    # core applications 
    url(r'^ref/', include('ref.urls')),
    url(r'^scm/', include('scm.urls')),
    
    # Login & co
    url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^accounts/scriptlogin/(?P<username>.*)/(?P<password>.*)$', ref_views.misc.script_login, name='script_login'),
    url(r'^accounts/scriptlogin$', ref_views.misc.script_login_post, name='script_login_post'),
    url(r'^accounts/forcelogging$', ref_views.misc.force_login, name='force_login'),
    url(r'^accounts/scriptlogout$', ref_views.misc.script_logout, name='script_logout'),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    url(r'^.*/logout/$', auth_views.LogoutView.as_view(next_page='/')),  # including admin logout
    
    # Admin & admin doc
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', site.urls),
    
    # Welcome screen (slash mapping)
    url(r'^$', projects, name='projects'),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [ path('__debug__/', include(debug_toolbar.urls)), ]
    except:
        pass
