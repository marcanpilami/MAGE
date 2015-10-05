# coding: utf-8
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import redirect_to_login
from django.db.transaction import atomic
from django.shortcuts import render_to_response, redirect
from ref.models.ou import PERMISSIONS, AclAuthorization, folder_permission_required
from ref.models.classifier import AdministrationUnit


@atomic
@folder_permission_required('change_permissions')
def set_acl(request, folder_id):
    folder = AdministrationUnit.objects.get(pk=folder_id)
    groups = Group.objects.order_by('name').all()

    if request.method == 'GET':
        acl = {}
        for ace in folder.acl.all():
            if acl.has_key(ace.group.name):
                acl[ace.group.name].append(ace.codename)
            else:
                acl[ace.group.name] = [ace.codename, ]

        groupsdic = {}
        for group in groups:
            groupsdic[group.id] = group.name

        return render_to_response('ref/acl_edit.html',
                                  {'folder': folder, 'groups': json.dumps(groupsdic), 'acl': json.dumps(acl),
                                   'perms': json.dumps(PERMISSIONS)})

    if request.method == 'POST':
        d = json.loads(request.body)
        for ace in folder.acl.all():
            ace.delete()

        for group_name, perm_list in d.items():
            if group_name == '_block' or len(perm_list) == 0:
                continue
            group = [g for g in groups if g.name == group_name][0]

            for perm in perm_list:
                AclAuthorization(target=folder, codename=perm, group=group).save()

        folder.block_inheritance = bool(d['_block'])

        return redirect("ref:set_acl", folder_id)


@atomic
@login_required
def remove_folder(request, folder_id):
    folder = AdministrationUnit.objects.get(pk=folder_id)
    parent_id = folder.parent_id

    if not request.user.has_perm('delete_folder', parent_id):
        return redirect_to_login(request.path)

    folder.delete()
    return redirect('ref:project_home', parent_id)
