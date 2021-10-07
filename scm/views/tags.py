# coding: utf-8

## Django imports
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render

## MAGE imports
from ref.models import Environment
from scm.models import Tag
from django.http.response import HttpResponse, HttpResponseNotFound
from MAGE.decorators import project_permission_required


def __tag_create(envt_name, tag_name):
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
    t.save()

    return t

@permission_required('scm.add_tag')
def tag_create(request, envt_name, tag_name):
    new_tag = __tag_create(envt_name, tag_name)
    return redirect('scm:tag_detail', tag_id=new_tag.id, project_id=request.project.pk)

@permission_required('scm.add_tag')
def tag_create_script(request, envt_name, tag_name):
    new_tag = __tag_create(envt_name, tag_name)
    return HttpResponse(new_tag.id, content_type='text/plain')

@permission_required('scm.add_tag')
def tag_remove(request, tag, redirect = True):
    try:
        t = Tag.objects.get(name=tag)
    except Tag.DoesNotExist:
        try:
            t = Tag.objects.get(pk=tag)
        except Tag.DoesNotExist:
            return HttpResponseNotFound('no tag with such a name or ID')

    t.delete()

    if redirect:
        return redirect('scm:tag_list')
    else:
        return HttpResponse(t.id, content_type='text/plain')

@permission_required('scm.add_tag')
def tag_remove_script(request, tag):
    tag_remove(request, tag, False)

def tag_detail(request, tag_id):
    t = Tag.objects.get(pk=tag_id)
    return render(request, 'scm/tag_detail.html', {'tag': t})

@project_permission_required
def tag_list(request):
    return render(request, 'scm/tag_list.html', {'tags': Tag.objects.filter(from_envt__project=request.project), 'project': request.project})
