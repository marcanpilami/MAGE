# coding: utf-8

"""
    MAGE backup sample module URL file.
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'list$',      'MAGE.sav.views.list_sav'),
    (r'del$',       'MAGE.sav.views.del_sav'),                     
)