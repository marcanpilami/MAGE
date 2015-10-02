# coding: utf-8
import json
from django.contrib.auth.models import Group
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
            if len(perm_list) == 0:
                continue
            group = [g for g in groups if g.name == group_name][0]

            for perm in perm_list:
                AclAuthorization(target=folder, codename=perm, group=group).save()
        return redirect("ref:set_acl", folder_id)
