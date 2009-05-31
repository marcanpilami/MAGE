# coding: utf-8

"""
    Graph module URL file.
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'full$',                                                                'MAGE.gph.views.full_pic'),
    (r'filter/(?P<nbParents>\d*)/(?P<nbPartners>\d*)/(?P<collapseThr>\d*)',   'MAGE.gph.views.filter_pic'),
    (r'graph$',                                                               'MAGE.gph.views.view_carto'),
    (r'envt/(?P<envt_id>\d*)/*$',                                             'MAGE.gph.views.envt_pic'),
  # (r'wk/(?P<wkf>.*)$',                                                      'MAGE.gph.views.view_workflow'),                         
)