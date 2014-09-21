# coding: utf-8

## Python imports
from time import timezone

## Django imports
from django import forms
from django.contrib.auth.decorators import permission_required
from django.utils.timezone import now
from django.shortcuts import render, redirect
from django.http.response import HttpResponse, HttpResponseBadRequest

## MAGE imports
from scm.backup import register_backup_envt_default_plan, register_backup
from scm.models import BackupSet, Environment, ComponentInstance


def backup_list(request, archive=False):
    return render(request, 'scm/backup_list.html', {'backups': BackupSet.objects.filter(removed__isnull=not archive).order_by('from_envt', 'set_date').select_related('all_items'), 'archive' : archive})

def backup_detail(request, bck_id):
    return render(request, 'scm/backup_detail.html', {'bck': BackupSet.objects.get(pk=bck_id)})

@permission_required('scm.add_backupset')
def backup_envt(request, envt_name):
    b = register_backup_envt_default_plan(envt_name, now())
    return redirect('scm:backup_detail', bck_id=b.id)

@permission_required('scm.add_backupset')
def backup_envt_manual(request, envt_name):
    e = Environment.objects.get(name=envt_name)

    if request.method == 'POST':  # If the form has been submitted...
        f = BackupForm(request.POST, envt=e)

        if f.is_valid():
            instances = ComponentInstance.objects.filter(pk__in=f.cleaned_data['instances'])
            bs = register_backup(e, f.cleaned_data['date'], "MANUAL - %s" % f.cleaned_data['description'], *instances)
            return redirect('scm:backup_detail', bck_id=bs.id)
    else:
        f = BackupForm(envt=e)

    return render(request, 'scm/backup_create_manual.html', {'form': f, 'envt': e})

@permission_required('scm.add_backupset')
def backup_script(request, envt_name, ci_id, bck_id=None):
    try:
        bs = register_backup(envt_name, now(), bck_id, ComponentInstance.objects.get(pk=ci_id), description='script backup')
        return HttpResponse(bs.id, content_type='text/text')
    except Exception, e:
        return HttpResponseBadRequest(e, content_type='text/text')


def backup_latest_age(request, ci_id):
    response = HttpResponse(content_type='text/text')
    try:
        ci = ComponentInstance.objects.get(pk=ci_id)
        bis = BackupSet.objects.filter(all_items__instance__id=ci.id)
        if bis.count() == 0:
            response.write("-1")
        else:
            bis = bis.latest('set_date')
            response.write(int(round((timezone.now() - bis.set_date).seconds / 60, 0)))
    except ComponentInstance.DoesNotExist, BackupSet.DoesNotExist:
        response.write("-1")
    return response



class BackupForm(forms.Form):
    description = forms.CharField(max_length=90, required=False)
    date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M', ])
    instances = forms.TypedMultipleChoiceField(choices=(), widget=forms.widgets.CheckboxSelectMultiple, coerce=int)

    def __init__(self, *args, **kwargs):
        self.envt = kwargs['envt']
        del kwargs['envt']
        super(BackupForm, self).__init__(*args, **kwargs)
        self.fields['instances'].choices = [(i.pk, i.__unicode__()) for i in self.envt.component_instances.all()]
