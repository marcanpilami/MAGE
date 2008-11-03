# coding: utf-8


## Python imports
from datetime import date

## Django imports
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from django.core.urlresolvers import reverse

## MAGE imports
from MAGE.sav.models import SaveSet


def list_sav(request):
    """Liste des sauvegardes disponibles"""
    sav_list = SaveSet.objects.all().filter(erased_on=None).order_by('from_envt.name').order_by('pk')
    return render_to_response('liste_saves.html', {'sav_list' : sav_list})


class DeleteSaveForm(forms.Form):
    save_to_kill = forms.ChoiceField(
            choices = [(e.pk, e.__unicode__()) for e in SaveSet.objects.all().filter(erased_on=None)], 
            widget = forms.widgets.Select,                    
            label = u'Sauvegarde à marquer comme supprimée :')


def del_sav(request):
    """Marquer manuellement une sauvegarde comme ayant été physiquement effacée."""
    if request.method == 'POST':                    # If the form has been submitted...
        form = DeleteSaveForm(request.POST)         # A form bound to the POST data
        if form.is_valid():                         # All validation rules pass
            # Process the data in form.cleaned_data
            id = form.cleaned_data['save_to_kill']
            ss = SaveSet.objects.get(pk=id)
            ss.erased_on = date.today()
            ss.save()
            return HttpResponseRedirect(reverse('MAGE.sav.views.del_sav')) # Redirect after POST
    else:
        form = DeleteSaveForm()                     # An unbound form

    return render_to_response('del_save.html', {'form': form, })
