#!/bin/python
# -*- coding: utf-8 -*-

## Setup django envt & django imports
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.db import transaction

## Python import
from optparse import OptionParser
import sys

## MAGE imports
from MAGE.ref.introspect import get_components_csv


def parseOptions():
    """Command line option parsing"""
    parser = OptionParser('ask_ref.py [-t] [-e ENVT] -c "name,parent_name,grandparent_name, ..." [-c "..."]')
    parser.add_option("-c", "--component", type="string", dest="components", action="append", 
                      help=u"designation du composant à décrire, sous la forme : name,parent_name,grandparent_name, ...\
                    Ou bien, simplement donner l'identifiant numérique unique du composant.")
    parser.add_option("-t", "--titles", action='store_true', dest="display_titles", default=False,
                      help=u'Afficher une liste des champs pour chaque composant')
    parser.add_option("-s", "--separator", type="string", dest="separator", default=";",
                      help=u'Séparateur de champs à utiliser')
    parser.add_option("-u", "--unique", action='store_true', dest="unique", default=False,
                      help=u'Sortie en erreur si plus d\'un résultat')
    
    return parser.parse_args()


def main():
    (options, args) = parseOptions()
    
    #print get_components_csv(descr, options.envt, options.display_titles) #debug (without any catching)
    res=""
    try:
        res += get_components_csv(options.components, options.display_titles, options.separator)
        if options.unique and ((options.display_titles and res.count('\n') > 0) or (not options.display_titles and res.count('\n') > 1)):
            raise Exception(u'Option unique precisee et plus d\'un resultat')
        print res
    except Exception, e:
        print e
        sys.exit(1)

if __name__ == "__main__":
    main()