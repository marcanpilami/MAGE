from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from ref.views import welcome

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MAGE.views.home', name='home'),
    # url(r'^MAGE/', include('MAGE.foo.urls')),

    # core applications 
    url(r'^gph/', include('gph.urls', namespace="gph")),
    url(r'^ref/', include('ref.urls', namespace="ref")),
    
    
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', welcome, name='welcome'),
    
    
)
