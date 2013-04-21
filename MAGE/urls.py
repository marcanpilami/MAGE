from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib.admin import autodiscover
from ref.admin import site 
autodiscover()

from ref.views import welcome

urlpatterns = patterns('',
    # core applications 
    url(r'^gph/', include('gph.urls', namespace="gph")),
    url(r'^ref/', include('ref.urls', namespace="ref")),
    url(r'^scm/', include('scm.urls', namespace="scm")),
    
    # Login & co
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^.*/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}), # including admin logout
    
    # Admin & admin doc
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #url(r'^admin/doc/', include('ref.admin.admin')),
    url(r'^admin/', include(site.urls)),
    
    # Welcome screen (slash mapping)
    url(r'^$', welcome, name='welcome'),
)
