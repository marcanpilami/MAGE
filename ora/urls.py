# coding: utf-8

"""
    Oracle database sample module URL file.
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""


from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'dba$', 'MAGE.ora.views.dba_edition'),
)