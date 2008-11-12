# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'list$',      'MAGE.sav.views.list_sav'),
    (r'del$',       'MAGE.sav.views.del_sav'),                     
)