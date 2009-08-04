#!/bin/python
# -*- coding: utf-8 -*-

## Setup django envt & django imports
from django.core.management import setup_environ
import settings
setup_environ(settings)

## Python import
from optparse import OptionParser
import sys

## Django imports
from django.db import transaction

## MAGE imports
from MAGE.ref.helpers import getMCL, getModel
from MAGE.ref.models import Environment


def parseOptions():
    """Command line option parsing"""
    parser = OptionParser('insert.py [ -e <ENVT_NAME> [ -e <ENVT2_NAME> ] ... ] [ -l <MCL> ] -a <ATTRIBUTE_NAME>=<VALUE> [ -a <ATTR_NAME2>=<VALUE2> [ ... ] ] -t <TYPE_COMPOSANT>')
    parser.add_option("-e", "--environment", type="string", action = "append", dest="envts", default = [],
                      help = u"Nom de l'environnement auquel ce composant appartient (optionnel)")
    parser.add_option("-l", "--link", type = "string", dest = "parents", action = "append",  default = [],
                      help = u"Description MCL des parents")
    parser.add_option("-a", "--attribute", type = "string", dest = "attributes", action = "append",
                      help = u"Attributs de l'objet à créer/mettre à jour, sous la forme CLE=VALEUR")
    parser.add_option("-t", "--type", type = "string", dest = "type",
                      help = u"Type de composant (i.e. nom de modèle)")
    parser.add_option("-k", "--keepparents", action = "store_true", dest = "keep_parents", default = False,
                      help = u"Dans le cas d'une mise à jour, conserver les parents existants (i.e. seulement ajouter ceux précisez par les options '-l')")
    parser.add_option("-c", "--component", type = "string", dest = "mcl",
                      help = u"Description MCL du composant à mettre à jour. Si non précisé, le script utilisera l'éventuelle clé pour identifier le composa,t. Si pas de clé, un nouveau composant sera toujours créé.")
    
    return parser.parse_args()


@transaction.commit_manually
def main():
    (options, args) = parseOptions()
    
    try:
        print u"Début ajout ou mise à jour d'un composant dans MAGE - début transaction."
        ## Order attributes
        attr = {}
        for elt in options.attributes:
            attr[elt.split('=')[0]] = elt.split('=')[1]
        
        ## Check compo existence
        print u"Recherche d'un éventuel composant existant dans la base"
        compo = None
        model_class = getModel(options.type)
        try:
            compo = getMCL(options.mcl).leaf
            print u'\tUn composant a été trouvé via la description MCL fournie'
        except:
            key = model_class.key
            key_req = {}
            for key_member in key:
                key_req[key_member] = attr[key_member]
            
            try:
                compo = model_class.objects.get(**key_req)
                print u'\tUn composant a été trouvé grace à la clé du modèle'
            except:
                print u"Composant pas trouvé. Sera donc créé."
            
        ## Update if necessary
        if compo:
            print u'Mise à jour du composant existant avec les attributs donnés'
            for (attribute, value) in attr.items():
                setattr(compo, attribute, value)
            compo.save()
        
        ## Create if necessary
        if not compo:
            print u'Création du composant avec tous les attributs donnés'
            compo = model_class(**attr)
            compo.save()
        
        ## Update links
        print u'Mise à jour des liens de parenté'
        if not options.keep_parents:
            print u'\tSuppression des liens de parenté existant'
            compo.dependsOn.clear()
        for mcl in options.parents:
            parent_compo = getMCL(mcl)
            if parent_compo not in compo.dependsOn.all():
                print u"\tLe composant est désormais un enfant du composant %s" %parent_compo
                compo.dependsOn.add(parent_compo)
        compo.save()
        
        ## Update environments
        print u'Mise à jour des environnements'
        compo.environments.clear()
        print u"\tSuppression des liens d'appartenance à des environnements existant" 
        for envt_name in options.envts:
            envt = Environment.objects.get(name = envt_name)
            print u"\tLe composant est désormais membre de l'environnement %s" %envt
            compo.environments.add(envt)
        compo.save()
        
    except Exception, e:
        print 'erreur - transaction annulée'
        print e      
        transaction.rollback()
        sys.exit(1)
    
    ## Correct end of script    
    transaction.commit()
    print u"Fin OK - transaction validée."


if __name__ == "__main__":
    main()
