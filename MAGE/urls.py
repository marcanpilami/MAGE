# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2022 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from django.urls import include, path, re_path
from django.contrib.admin import autodiscover
from django.contrib.auth import views as auth_views
from ref.admin import site
from django.conf import settings
autodiscover()
from ref.views.misc import welcome
from ref import views as ref_views

urlpatterns = [
    # core applications
    re_path(r'^ref/', include('ref.urls')),
    re_path(r'^scm/', include('scm.urls')),

    # Login & co
    re_path(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    re_path(r'^accounts/scriptlogin/(?P<username>.*)/(?P<password>.*)$', ref_views.misc.script_login, name='script_login'),
    re_path(r'^accounts/scriptlogin$', ref_views.misc.script_login_post, name='script_login_post'),
    re_path(r'^accounts/forcelogging$', ref_views.misc.force_login, name='force_login'),
    re_path(r'^accounts/scriptlogout$', ref_views.misc.script_logout, name='script_logout'),
    re_path(r'^accounts/logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    re_path(r'^.*/logout/$', auth_views.LogoutView.as_view(next_page='/')),  # including admin logout
    
    # Admin & admin doc
    re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    re_path(r'^admin/', site.urls),
    
    # Welcome screen (slash mapping)
    re_path(r'^$', welcome, name='welcome'),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [ path('__debug__/', include(debug_toolbar.urls)), ]
    except:
        pass
