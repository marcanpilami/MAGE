# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Python imports
from datetime import timedelta

## MAGE imports
from MAGE.exceptions import MageCallerError
from ref.models import Environment
from scm.models import BackupSet, BackupItem, InstallableItem, BackupRestoreMethod
from ref.models.parameters import getParam

def register_backup(envt, backup_date, bck_id, *component_instances, **kwargs):
    ## Check params
    if isinstance(envt, str):
        envt = Environment.objects.get(name=envt)
    
    for instance in component_instances:
        if instance.environments.count() > 0 and (not (instance.environments.filter(pk=envt.id).exists())):
            raise MageCallerError('instance does not belong to the specified environment')
    
    bck_name = "BACKUP_%s_%s" % (envt.name, backup_date.strftime('%Y%m%d%H%M'))
    i = BackupSet.objects.filter(name__startswith=bck_name).count()
    if i > 0:
        bck_name = "%s_%s" % (bck_name, i)
    
    bs = None
    if bck_id is None:
        # Check if we should merge the backupset with an ongoing one
        limit = int(getParam('BACKUP_MERGE_LIMIT'))
        tlimit1 = backup_date - timedelta(minutes=limit)
        tlimit2 = backup_date + timedelta(minutes=limit)
        backups = BackupSet.objects.filter(from_envt = envt, set_date__lte = tlimit2, set_date__gte = tlimit1)
        if limit != 0 and backups.count() > 0:
            ## If here, there are backups made on the same environment recently. Check the instances are not already backuped.
            for bck in backups:
                for ci_id in [ci.pk for ci in component_instances]:
                    potential = True
                    if ci_id in [i.instance_id for i in bck.all_items.all()]:
                        potential = False
                        break
                if potential:
                    bs = bck
                 
        # No merge: create a new backupset
        if bs is None:
            if not 'description' in kwargs:
                kwargs['description']='backup taken from environment %s on %s' % (envt.name, backup_date)
            bs = BackupSet(name=bck_name, status=1, from_envt=envt, **kwargs)
            bs.save()
    else:
        bs = BackupSet.objects.get(pk = bck_id)
    
    for ci in component_instances:
        c = ci.cic_at_safe(backup_date)
        v = ci.version_at_safe(backup_date)
        if v is None:
            bi = BackupItem(backupset=bs , instance=ci)
            bi.save()
        else:
            ii = InstallableItem(what_is_installed=v, belongs_to_set=bs, is_full=True, data_loss = True)
            ii.save()
            bmr = BackupRestoreMethod.objects.filter(target=ci.instanciates, method__available = True)[0] # admin forbids creating more than one
            ii.how_to_install.add(bmr.method)
            bi = BackupItem(backupset=bs, instance=ci, related_scm_install=ii, instance_configuration=c)
            bi.save()
            
    return bs


def register_backup_envt_default_plan(envt_name, backup_date):
    e = Environment.objects.get(name=envt_name)
    return register_backup(e, backup_date, None, * e.component_instances.filter(include_in_envt_backup=True), description = "default plan backup")

    