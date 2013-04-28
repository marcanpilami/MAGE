# coding: utf-8
from ref.models import Environment
from MAGE.exceptions import MageCallerError
from scm.models import BackupSet, BackupItem, InstallableItem, BackupRestoreMethod

def register_backup(envt, backup_date, *component_instances):
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
    
    bs = BackupSet(name=bck_name, description='backup taken from environment %s on %s' % (envt.name, backup_date), status=1, from_envt=envt)
    bs.save()
    
    for ci in component_instances:
        c = ci.cic_at_safe(backup_date)
        v = ci.version_at_safe(backup_date)
        if v is None:
            bi = BackupItem(backupset=bs , instance=ci)
            bi.save()        
        else:
            ii = InstallableItem(what_is_installed=v, belongs_to_set=bs, is_full=True)
            ii.save()
            bmr = BackupRestoreMethod.objects.filter(target=ci.instanciates, apply_to=envt, method__available = True)[0]
            ii.how_to_install.add(bmr.method)
            bi = BackupItem(backupset=bs , instance=ci, related_scm_install=ii, instance_configuration=c)
            bi.save()
            
    return bs


def register_backup_envt_default_plan(envt_name, backup_date):
    e = Environment.objects.get(name=envt_name)
    return register_backup(e, backup_date, * e.component_instances.filter(include_in_envt_backup=True))
