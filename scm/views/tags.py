# coding: utf-8

## Django imports
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render

## MAGE imports
from ref.models import Environment
from scm.models import Tag
from django.http.response import HttpResponseNotFound


@permission_required('scm.add_tag')
def tag_create(request, envt_name, tag_name):
    e = Environment.objects.get(name=envt_name)

    tt = Tag.objects.filter(name__contains=tag_name).count()
    if tt > 0:
        tag_name = "%s_%s " % (tag_name, tt)

    t = Tag(name=tag_name, from_envt=e)
    t.save()

    for instance in e.component_instances.all():
        v = instance.version_object_safe
        if v is not None:
            t.versions.add(v)

    return redirect('scm:tag_detail', tag_id=t.id)

@permission_required('scm.add_tag')
def tag_remove(request, tag):
    try:
        t = Tag.objects.get(name=tag)
    except Tag.DoesNotExist:
        try:
            t = Tag.objects.get(pk=tag)
        except Tag.DoesNotExist:
            return HttpResponseNotFound('no tag with such a name or ID')

    t.delete()
    return redirect('scm:tag_list')


def tag_detail(request, tag_id):
    t = Tag.objects.get(pk=tag_id)
    return render(request, 'scm/tag_detail.html', {'tag': t})

def tag_list(request, project):
    return render(request, 'scm/tag_list.html', {'tags': Tag.objects.filter(from_envt__project__name=project), 'project': project})
