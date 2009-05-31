# coding: utf-8

"""
    Oracle database sample module views file.
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Django imports
from django.shortcuts import render_to_response

## MAGE imports
from MAGE.ora.models import OracleInstance, OracleSchema
    
def dba_edition(request):
    """Liste des schémas par instance Oracle"""
    instance_set = OracleInstance.objects.all()
    unclassified_schemas = OracleSchema.objects.all().exclude(dependsOn__model__model='oracleinstance') 
    return render_to_response('ora_dba_edition.html', {'instance_set':instance_set, 'us':unclassified_schemas})


