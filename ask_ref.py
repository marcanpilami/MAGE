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
    parser.add_option("-e", "--envt", type="string", dest="envt", 
                      help=u"environnement contenant les composants (optionel)")
    parser.add_option("-c", "--component", type="string", dest="components", action="append", 
                      help=u"designation du composant à décrire, sous la forme : name,parent_name,grandparent_name, ...\
                    Ou bien, simplement donner l'identifiant numérique unique du composant.")
    parser.add_option("-t", "--titles", action='store_true', dest="display_titles", default=False,
                      help=u'Afficher une liste des champs pour chaque composant')
    
    return parser.parse_args()


def main():
    (options, args) = parseOptions()
    descr = [i.split(',') for i in options.components]
    #print get_components_csv(descr, options.envt, options.display_titles) #debug (without any catching)
    try:
        print get_components_csv(descr, options.envt, options.display_titles)
    except Exception, e:
        print e
        sys.exit(1)

if __name__ == "__main__":
    main()