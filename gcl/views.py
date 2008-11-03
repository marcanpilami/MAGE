# coding: utf-8

## Python imports

## Django imports
from django.http import HttpResponse
from django.shortcuts import render_to_response

## MAGE imports
from MAGE.gcl.models import Installation, Tag, ComponentTypeVersion, Component
from MAGE.liv.models import Delivery 


def installs_list_envt(request, envt_name):
    install_list = Installation.objects.filter(target_envt__name = envt_name).order_by('install_date')
    return render_to_response('install_list.html', {'install_list' : install_list, 'envt_name': envt_name})


def tag_list(request):
    """Liste des niveaux applicatifs de référence"""
    tag_list = Tag.objects.order_by('snapshot_date')
    return render_to_response('tags_list.html', {'tag_list' : tag_list })

def installs_comp(request, compoID):
    install_list = Installation.objects.filter(target_components__pk = compoID).order_by('install_date')
    compo = Component.objects.get(pk=compoID)
    return render_to_response('component_installs.html', {'install_list' : install_list, 'compo': compo})

def delivery_list(request):
    """Liste des livraisons disponibles"""
    dl = Delivery.objects.all()
    return render_to_response('del_list.html', {'del_list' : dl, })

def version_list(request):
    """Liste classée des différentes versions de composant d'environnement connues du système.
    En l'état, c'est surtout un test de la relation d'ordre des versions."""
    list1 = [i for i in ComponentTypeVersion.objects.all()]#filter(class_name='@TRUC')]
    list1.sort(cmp=ComponentTypeVersion.compare)
    list2 = [i for i in ComponentTypeVersion.objects.all()]#filter(class_name='@TRUC')]
    list2.sort(cmp=ComponentTypeVersion.compare, reverse=True)
    
    return render_to_response('ctv_list.html', {'list1': list1, 'list2':list2})