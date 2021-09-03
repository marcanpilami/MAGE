# coding: utf-8

from django.http.response import HttpResponse
from django.shortcuts import render
from django import forms
from ref import mql
import unicodecsv as csv
import json


class MqlTesterForm(forms.Form):
    mql = forms.CharField(max_length=300, initial='SELECT INSTANCES', label='Requête MQL', widget=forms.TextInput(
                 attrs={'size':'200', 'class':'inputText'}))

def mql_tester(request, project):
    base = request.build_absolute_uri('/')[:-1]
    error = None
    if request.method == 'POST': # If the form has been submitted...
        form = MqlTesterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                res = mql.run(form.cleaned_data['mql'], project, return_sensitive_data = request.user.has_perm('ref.allfields_componentinstance'))
                return render(request, 'ref/mql_tester.html', {'mql': form.cleaned_data['mql'], 'form': form, 'results': res, 'base': base, 'project': project})
            except Exception as e:
                error = e.__str__()
    else:
        form = MqlTesterForm() # An unbound form

    return render(request, 'ref/mql_tester.html', {'form': form, 'base': base, 'error': error, 'project': project})

def mql_query(request, output_format, project, query):
    res = mql.run(query, project, return_sensitive_data = request.user.has_perm('ref.allfields_componentinstance'))

    if output_format == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="result.csv"'
        dd = {}
        for it in res:
            for k in it.keys():
                dd[k] = None
        wr = csv.DictWriter(response, fieldnames=dd.keys(), restval="", extrasaction='ignore', dialect='excel', delimiter=";")
        wr.writeheader()
        wr.writerows(res)
        return response
    
    if output_format == 'sh':
        return render(request, 'ref/mql_export_sh.html', {'instances': res}, content_type="text/plain")
    
    if output_format == 'bash4':
        return render(request, 'ref/mql_export_bash4.html', {'instances': res}, content_type="text/plain")
    
    if output_format == 'json':
        response = HttpResponse(content_type='text/json; charset=utf-8')
        json.dump(res, fp = response, ensure_ascii = False, indent= 4)
        return response

