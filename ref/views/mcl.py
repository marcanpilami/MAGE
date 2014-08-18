# coding: utf-8

from django.http.response import HttpResponse
from ref.csvi import get_components_csv, get_components_pairs
from ref.mcl import parser
from django.shortcuts import render
from ref.creation import create_instance
from MAGE.exceptions import MageCallerError
from django import forms


class MclTesterForm(forms.Form):
    mcl = forms.CharField(max_length=300, initial='()', label='Requête MCL', widget=forms.TextInput(
                 attrs={'size':'200', 'class':'inputText'}))
    allow_creation = forms.BooleanField(initial=False, required=False)

def mcl_tester(request):
    base = request.build_absolute_uri('/')[:-1]
    error = None
    if request.method == 'POST': # If the form has been submitted...
        form = MclTesterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                res = parser.get_components(form.cleaned_data['mcl'], allow_create=form.cleaned_data['allow_creation'])
                return render(request, 'ref/mcltester.html', {'mcl': form.cleaned_data['mcl'], 'form': form, 'results': res, 'base': base})
            except MageCallerError, e:
                error = e.message
    else:
        form = MclTesterForm() # An unbound form

    return render(request, 'ref/mcltester.html', {'form': form, 'base': base, 'error': error})

def mcl_query(request, mcl, titles='1'):
    res = parser.get_components(mcl)
    if titles == '1':
        titles = True
    else:
        titles = False

    response = HttpResponse(content_type='text/csv')
    get_components_csv(res, titles, response, displayRestricted=(request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance')))
    return response


def mcl_query_shell(request, mcl):
    res = parser.get_components(mcl)
    compos = get_components_pairs(res, request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance'))
    return render(request, 'ref/shell_mcl_result_ksh.html', {'attrs': compos}, content_type="text/text")

def mcl_create(request, mcl, use_convention='1'):
    if use_convention == '1':
        use_convention = True
    else:
        use_convention = False
    res = create_instance(mcl, use_convention)

    response = HttpResponse(content_type='text/csv')
    get_components_csv(res, True, response, displayRestricted=(request.user.is_authenticated() and request.user.has_perm('ref.allfields_componentinstance')))
    return response


def mcl_create_without_convention(request, mcl):
    return mcl_create(request, mcl, '0')

