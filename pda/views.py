# coding: utf-8

"""
    MAGE main page module
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Django imports
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

## MAGE imports
from MAGE.ref.models import *


def page_de_garde(request):
    """Page présentant le détail de tous les environnements"""
    envts = Environment.objects.all()
    return render_to_response('accueil.html', {'envts':envts})


class InternalPage:
    def __init__(self):
        self.url = ""
        self.name = ""
        self.doc = ""
        self.appli = ""

def liste_pages(request):
    """Liste des pages web (ie. vues Django ne prenant pas de paramètres)"""
    from django.conf import settings
    from django.core.urlresolvers import RegexURLResolver
    urlconf = settings.ROOT_URLCONF
    urlconf_module = __import__(urlconf, {}, {}, [''])
    pages = []
    
    patterns = urlconf_module.urlpatterns
    
    for regobj in patterns:
        ## Recursive exploration of included urlconf
        if isinstance(regobj, RegexURLResolver):
            patterns += regobj.url_patterns
            continue
        
        ## Django pages exceptions 
        if regobj.callback.__name__ == 'root' or regobj.callback.__name__ == 'serve':
            continue
        
        ## Already in the list ?
        if [pa.name for pa in pages].__contains__(regobj.callback.__name__):
            continue
        
        ## Test args number
        try:
            url = reverse(regobj.callback)
        except:
            continue
         
        ## It's a page to display => to the list !
        ip = InternalPage()
        ip.name = regobj.name or regobj.callback.__name__
        ip.doc = regobj.callback.__doc__ or u'Pas de description disponible'
        ip.url = url
        ip.appli = regobj.callback.__module__.split(".")[1]
        pages.append(ip)
    
    return render_to_response('liste_pages.html', {'pages':pages})