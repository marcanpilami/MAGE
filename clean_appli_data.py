# coding: utf-8

## Setup Django envt
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.db import models
models.get_apps()


## Python imports
from optparse import OptionParser

## Django imports
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

## MAGE imports
from MAGE.ref.models import Component, MageModelType
from MAGE.prm.models import MageParam


def parseOptions():
    """Command line option parsing"""
    parser = OptionParser('clean_appli_data.py -a appli')
    parser.add_option("-a", "--application", type="string", dest="appli", 
                      help=u"application dont il faut effacer les éléments")
    return parser.parse_args()


@transaction.commit_manually
def delete_all_objects_in_app(app):
    ## Delete all model instances
    print u'Début effacement des objets relatifs à %s' %app
    for ct in ContentType.objects.filter(app_label = app):
        model_class = ct.model_class()
        i=0
        print u'        effacement des objets de modèle %s' %model_class.__name__.lower()
        for object in model_class.objects.all():
            object.delete()
            i = i+1
        
        for object in MageModelType.objects.filter(name = model_class.__name__.lower()):
            object.delete()
        
        ct.delete()
        print '%s objets effacés' %i
    
    ## Delete all params
    i=0
    print u'Début effacement des paramètres relatifs à %s' %app
    for param in MageParam.objects.filter(app = app):
        param.delete()
        i=i+1
    print '%s paramètres effacés' %i

    
    
    transaction.commit()


def main():
    ## Parse arguments
    (options, args) = parseOptions()
    
    ## Delete everything
    delete_all_objects_in_app(options.appli)


if __name__ == "__main__":
    main()