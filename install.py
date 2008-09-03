#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    InstallableSet installation registration interface.
    
    It requires associations between [envt components] and [the different CTVs of the IS] 
    A component is identified by its name, then by the name of its ancestors.
    A non-existing component can be described, provided all its required_ancestors are given. It will then be created.
    
    install.py -e ENVT -i (IS_ID|IS_NAME) -c "type_composant,name=value,[parent_name=value[,grand_parent_name=value2,...]]" [-c ...] [-f]
    
    @author: mag
""" 

#TODO: policer les exceptions en n'affichant que le message d'erreur proprement dit.

## Setup django envt & django imports
from django.core.management import setup_environ
import settings
setup_environ(settings)


## Python import
from time import strftime
from optparse import OptionParser
from sys import exit

## MAGE imports
import MAGE.ref.helpers
from MAGE.liv.models import *
from MAGE.gcl.models import *
from MAGE.ref.models import *
from MAGE.gcl.helpers import arePrerequisitesVerified


def parseOptions():
    """Command line option parsing"""
    parser = OptionParser('install.py -e ENVT -c "CTV_ID,parent_name=value[,...]" [-c "..."] -i INSTALLSET_NAME [-t]')
    parser.add_option("-e", "--envt", type="string", dest="envt", 
                      help=u"environnement sur lequel installer")
    parser.add_option("-c", "--component", type="string", dest="components", action="append", 
                      help=u"description du composant à mettre à jour à l'aide du patch ou de la sauvegarde désigné")
    parser.add_option("-i", "--installset", type="string", dest="isid", 
                      help=u"nom du patch ou de la sauvegarde à installer (ou bien son ID numérique)")
    parser.add_option("-t", "--test", action="store_true", dest="test", default=False, 
                      help=u"ne faire que les tests d'installabilité, pas le référencement")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, 
                      help=u"afficher des informations")
    parser.add_option("-f", "--force", action="store_true", dest="force", default=False, 
                      help=u"forcer l'installation même si les prérequis en sont pas vérifiés, \
                      ou si la livraison est DELTA et que le composant n'existe pas")
    return parser.parse_args()


#Règle : les seuls print autorisés sont dans main. Le reste se fait via exceptions.
def main():
    """Main function"""
    
    ## Helper vars
    new_compos = []
    
    ## Parse arguments
    (options, args) = parseOptions()
    
    ## Extract compo description and Compo/CTV associations (in lists: order is important)
    if options.components:
        compo_list = [l.split(',') for l in options.components]
    else:
        print u"Indiquez au moins un composant (option -c)"
        exit(1)

    ## Resolve IS (by name or by ID)
    try:
        is_source = InstallableSet.objects.get(name=options.isid)
    except InstallableSet.DoesNotExist:
        try:
            is_source = InstallableSet.objects.get(pk=options.isid)
        except InstallableSet.DoesNotExist:
            print u"L'identifiant de la livraison à installer est incorrect, ou elle n'est pas référencée." 
            exit(1)
    
    ## Resolve envt    
    try:
        envt = Environment.objects.get(name=options.envt)
    except Environment.DoesNotExist:
        print u"Environnement inconnu"
        exit(1)
    
    ## Check the prerequisites for this IS on the given envt.
    if not arePrerequisitesVerified(options.envt, is_source) and not options.force:
        print u"Les prérequis ne sont pas vérifiés ! Précisez l'option -f pour passer outre."
        exit(1)
    if not arePrerequisitesVerified(options.envt, is_source) and options.force:
        print u"Les prérequis ne sont pas vérifiés ! L'option -f étant précisée, le script passe outre."
    
    ## Loop on components
    for compo_descr in compo_list:
        compo_type_name = compo_descr[0]
        compo_name = compo_descr[1].split('=')[1]
        
        ## Find a CTV in the patch corresponding to the compo name, compo type, IS.
        try:
            ctv=ComponentTypeVersion.objects.get(component_type__model=compo_descr[0],component_name=compo_name,\
                                                 installableset=is_source)
        except ComponentTypeVersion.DoesNotExist:
            print u'Les composants %s de type %s ne sont pas concernés par la livraison %s' %(compo_type_name, compo_name, is_source.name)
            cleanNewCompos(new_compos)
            exit(1)
        compo_descr[0]=ctv
        
        ## Find the component
        try:
            compo = MAGE.ref.helpers.getComponent(compo_type_name, compo_descr[1:], envt.name)
        except MAGE.ref.helpers.UnknownComponent:
            ## No component could be found. Should it be created ?
            if not is_source.is_full and not options.force:
                print u"Le composant décrit par %s n'existe pas, et ne peut être créé par une livraison \
                de type mise à jour. Précisez l'option -f pour forcer la tentative de création." %(compo_descr)
                exit (1)
            if not is_source.is_full and options.force:
                print u"Le composant décrit par %s n'existe pas, et ne dvrait pas être créé par une livraison \
                de type mise à jour. L'option -f ayant été précisée, sa création sera néanmoins tentée." %(compo_descr)
            
            ## Build new compo
            try:
                compo = MAGE.ref.helpers.findOrCreateComponent(compo_type_name, compo_descr[1:], envt.name) # Raises exceptions
                new_compos.append(compo)                                                                    # For rollback
            except:
                cleanNewCompos(new_compos)
                raise
        
        ## Update the list : replace the component description by the component itself.
        del compo_descr[1:]
        compo_descr.append(compo.leaf)
    ## compo_list is now a list of pairs [ [CTV, Component], ...]
    
    
    ## If test run => exit now
    if options.test:
        exit(0)
    
    ## Registration itself
    try:
        i = Installation(installed_set=is_source, target_envt=envt, install_date=strftime('%Y-%m-%d %H:%M'))
        i.save()
        for pair in compo_list:
            cv = ComponentVersion(version = pair[0], component = pair[1], installation = i)
            cv.save()
        i.save()
    except:
        cleanNewCompos(new_compos)
        i.delete()
        print u"Impossible d'enregistrer l'installation"
        raise


def cleanNewCompos(new_compos):
    for compo in new_compos:
        compo.delete()
        
if __name__ == "__main__":
    main()
