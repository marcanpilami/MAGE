#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    InstallableSet installation registration interface.
    
    It requires associations between [envt compoennts] and [the different CTVs of the IS] 
    A component is identified by its name, then by the name of its ancestors.
    A non-existing component can be described, provided all its required_ancestors are given. It will then be created.
    
    install.py -e ENVT -i IS_ID -c "CTV_ID,parent_name=value[,grand_parent_name=value2,...]" [-c ...]
    
    @author: mag
""" 

## Setup django envt
from django.core.management import setup_environ
import settings
setup_environ(settings)

## Python import
from time import strftime
from optparse import OptionParser
from sys import exit

## MAGE imports
from MAGE.liv.models import *
from MAGE.gcl.models import *
from MAGE.ref.models import *

## parse arguments

def parseOptions():
    """Command line option parsing"""
    parser = OptionParser('install.py -e ENVT -c "CTV_ID,parent_name=value[,...]" [-c "..."] -i INSTALLSET_NAME [-t]')
    parser.add_option("-e", "--envt", type="string", dest="envt", 
                      help=u"environnement sur lequel installer")
    parser.add_option("-c", "--component", type="string", dest="components", action="append", 
                      help=u"composant à mettre à jour à l'aide du CTV désigné")
    parser.add_option("-i", "--installset", type="string", dest="isid", 
                      help=u"nom du patch ou de la sauvegarde à installer")
    parser.add_option("-t", "--test", action="store_true", dest="test", default=False, 
                      help=u"ne faire que les tests d'installabilité, pas le référencement")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, 
                      help=u"afficher des informations")
    parser.add_option("-f", "--force", action="store_true", dest="force", default=False, 
                      help=u"forcer l'installation même si les prérequis en sont pas vérifiés")
    return parser.parse_args()

def main():
    """Main function"""
    #TODO: This horrible stuff should be split into small pieces
    
    (options, args)=parseOptions()
    
    ## Extract compo description and Compo/CTV associations (in lists: order is important)
    if options.components:
        compo_list = [l.split(',') for l in options.components]
    else:
        print u"Indiquez au moins un composant"
        exit(1)

    ## Resolve CTVs
    for compo_descr in compo_list:
        try:
            compo_descr[0] = ComponentTypeVersion.objects.get(pk=compo_descr[0])
        except ComponentTypeVersion.DoesNotExist:
            print u"Le CTV n°%s n'existe pas." % compo_descr[0]
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
    
    #TODO: Check CTV in the IS
    
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
    
    ## Resolve components
    for compo_descr in compo_list:
        compo_type = compo_descr[0].component_type
        compo_name = compo_descr[0].component_name
        rs = Composant.objects.filter(environments__name=options.envt, type=compo_type, name=compo_name)
        
        ## Selection through parents
        curExampleCompo = rs.all()[0].leaf ## hack : this is a means to access subclass properties. Other solution : use an exec("import " + compo_type_path)
        i = 1
        while i < len(compo_descr) and rs.count() > 1: # and rs.count() > 1
            field, sep, value = compo_descr[i].partition('=')
            
            parents = curExampleCompo.parents
            try:
                nextExampleCompo = getattr(curExampleCompo, field).leaf
                parentModel = parents[field]
            except :
                print u"Les composants de type %s n'ont pas de parent %s" %(curExampleCompo.type.name, field)
                exit(1)
            
            ## Query construction
            d = {}
            papa = ""
            for p in range(0,i):
                papa = papa + "dependsOn__"
            #d[papa + 'type'] = MageModelType.objects.get(model=parentModel.lower()) # Django bug (#8046) ??? name alone should be enough
            d[papa +'name'] = value
            
            ## Query
            rs = rs.filter(**d)
            
            ## Iteration
            i=i+1
            curExampleCompo = nextExampleCompo
     
        if rs.count() > 1:
            print u"Il y a plus d'un composant répondant à la description %s. Précisez !" %(compo_descr)
            exit(1)
        
        compo = None   
        new_compos = [] 
        if rs.count() == 0:
            ## No component could be found. Should it be created ?
            if not is_source.is_full:
                print u"Le composant décrit par %s n'existe pas, et ne peut être créé par une livraison de type mise à jour." %(compo_descr)
                exit (1)
            try:
                compo = createAComponent(compo_descr) #TODO: write the function
                new_compos.append(compo)
            except:
                cleanNewCompos()
                print u"Impossible de créer le nouveau composant %s" % compo_descr
                exit(1)
        else:
            ## The component was found without ambiguities.
            compo = rs.all()[0]
        
        ## Update the list : replace the component description by the component itself.
        del compo_descr[1:]
        compo_descr.append(compo.leaf)
    
    
    ## Check compatibility between IS/CTV and the envt
    for pair in compo_list:
        if pair[0].component_type != pair[1].type:
            print u"On ne peut installer un élément %s sur un composant de type %s !" \
                %(pair[0].component_type, pair[1].type)
            cleanNewCompos()
            exit(1)
    
    ## If test run => exit
    if options.test:
        exit(0)
    print compo_list
    
    ## Registration
    try:
        i = Installation(installed_set=is_source, target_envt=envt, install_date=strftime('%Y-%m-%d %H:%M'))
        i.save()
        for pair in compo_list:
            cv = ComponentVersion(version = pair[0], component = pair[1], installation = i)
            cv.save()
        i.save()
    except:
        cleanNewCompos()
        i.delete()
        print u"Impossible d'enregistrer l'installation"
        raise



def cleanNewCompos():
    for compo in new_compos:
        compo.delete()
        
## Global compat test
def arePrerequisitesVerified(envt_name, is_tocheck):
    ok = True
    for prereq in is_tocheck.requirements.all():
        rs = Composant.objects.filter(environments__name=envt_name, name=prereq.component_name, type=prereq.component_type)
        if rs.count() == 0:
            print u"L'IS %s a besoin d'au moins un composant de type %s en version %s, mais ce type de composant \
                n'existe pas dans l'environnement %s" %(prereq.component_type, prereq.version, envt_name) 
            ok = False
        for compo in rs.all():
            if compo.version != prereq.version:
                print u"Le composant %s est en version %s, alors que l'installation requiert la version %s" \
                    %(compo, compo.version, prereq.version)
                ok = False
    return ok


def createAComponent(compo_descr):
    return

if __name__ == "__main__":
    main()
