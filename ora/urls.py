# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'dba$', 'MAGE.ora.views.dba_edition'),
)