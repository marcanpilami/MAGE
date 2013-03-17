from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from ref.views import welcome

urlpatterns = patterns('',
    # core applications 
    url(r'^gph/', include('gph.urls', namespace="gph")),
    url(r'^ref/', include('ref.urls', namespace="ref")),
    
    # Admin & admin doc
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    # Welcome screen (slash mapping)
    url(r'^$', welcome, name='welcome'),
)
