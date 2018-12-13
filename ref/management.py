# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Python imports

## Django imports
from django.db.models.signals import post_migrate

## MAGE imports
from ref.models.parameters import setOrCreateParam


def post_migrate_handler(sender, **kwargs):
    ## Create or update parameters

    ## General parameters that should never be removed...
    setOrCreateParam(key=u'LINK_COLORS', value=u'#004D60,#1B58B8,#DE4AAD,#D39D09,#AD103C,#180052',
             default_value=u'#004D60,#1B58B8,#DE4AAD',
             description=u'Couleurs des liens de la page d\'accueil')

    setOrCreateParam(key=u'MODERN_COLORS', value=u'#004A00,#61292B,#180052,#AD103C,#004D60,#1B58B8,#DE4AAD',
             default_value=u'#004A00,#61292B,#180052,#AD103C,#004D60,#1B58B8,#DE4AAD',
             description=u'Couleurs des cases de la page d\'accueil')

    ## Welcome screen parameters
    setOrCreateParam(key=u'LINKS_TITLE', value='Liens utiles',
             default_value='Liens utiles',
             description=u'titre du bloc de liens sur la page d\'accueil',
             axis1='welcome')

    ## DEBUG
    #create_full_test_data()


"""
C:\Python27\python.exe .\manage.py sqlclear ref,scm | select-string -NotMatch dot  | C:\Python27\python.exe .\manage.py dbshell
C:\Python27\python.exe .\manage.py migrate
C:\Python27\python.exe .\manage.py runserver
"""


"""
from ref.models import  *
p = ComponentInstance.objects.all()[1]
c = p.build_proxy()
c.admin_login
c.server_name
"""

# ((T,oracleinstance)(S,admin_login="login",admin_password="password")(R,server,((S,dns="server.marsu.net"))))

''' 
from ref.models import  *
c = ComponentInstance.objects.filter(description__name='jbossapplication')[0]
p = c.proxy
s = ComponentInstance.objects.filter(description__name='oracleschema')[0]
p.schema.append(s)
p.schema[0]
'''
