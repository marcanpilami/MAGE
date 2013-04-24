# coding: utf-8
from ref.models import Environment
from MAGE.exceptions import MageCallerError

def register_backup(envt, *component_instances):
    ## Check params
    if isinstance(envt, str):
        envt = Environment.objects.get(name = envt)
    
    for instance in component_instances:
        if instance.environments.count() > 0 and not instance.environments.filter(id == envt.id).exists():
            raise MageCallerError('instance does not belong to the specified environment')
    
    