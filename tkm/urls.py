# coding: utf-8

"""
    Minimalist Ticket Manager URL.
    
    @warning: This is not done, and should no be used. (and is of little interest)
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'newticket[/(?P<ticket_class>.*)]{0,1}', 'MAGE.tkm.views.new_ticket'),
    (r'list[/(?P<summary_name>.*)]{0,1}', 'MAGE.tkm.views.summary'),
    (r'view/(?P<ticket_id>\d*)', 'MAGE.tkm.views.edit_ticket'),
    (r'setperm', 'MAGE.tkm.views.set_permissions'),
)