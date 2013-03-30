'''
Created on 23 mars 2013

@author: Marc-Antoine
'''

import datetime

from django.contrib.contenttypes.models import ContentType

from ref.models import NamingConvention, NamingConventionField, ComponentInstance, \
    NamingConventionCounter
from django.db.models.fields.related import ManyToManyField, ForeignKey
from MAGE.exceptions import MageError

def nc_sync_naming_convention(nc, model_name_list=None):
    cts = None
    if model_name_list is None or len(model_name_list) == 0:
        cts = ContentType.objects.all()
    else:
        cts = ContentType.objects.filter(model__in=model_name_list)
    
    for ct in cts:
        # Only for component instances
        if ct.model_class().__bases__[0] != ComponentInstance:
            continue

        # Loop on fields so as to create an empty convention for each
        for fn in ct.model_class()._meta.get_all_field_names():
            # Get the field object - it may be a field on a related model
            field_descr = ct.model_class()._meta.get_field_by_name(fn)
            field = field_descr[0]
            if not field_descr[2]: # direct or related?
                field = field.field
            
            # No generic field
            if fn in ('dependsOn', 'model', 'pedestals_ci2do', 'statues_ci2do', 'environments', 'configurations', 'subscribers'):
                continue
            
            # Only true model fields
            if field.auto_created or not field.editable:
                continue
            
            # Already exists ?
            if nc.fields.filter(field=fn, model=ct.model).exists():
                continue
            
            # Create a convention for the field
            ptype = 'P'
            if fn == 'instanciates':
                ptype = 'CIC'
            elif isinstance(field, ForeignKey):
                ptype = 'MCL1'
            elif  isinstance(field, ManyToManyField):
                ptype = 'MCL0'
                
            ncf = NamingConventionField(model=ct.model, field=fn, pattern=None, pattern_type=ptype, convention_set=nc)
            ncf.save()
            
        # Loop on dependsOn elements so as to create an empty convention for each
        for k, v in ct.model_class().parents.items():
            # Already exists ?
            if nc.fields.filter(field=k, model=ct.model).exists():
                continue
            
            # Create the convention
            ptype = 'MCL0'
            f_card = v.get('card') or 1
            if f_card == 1:
                ptype = 'MCL1'
                
            ncf = NamingConventionField(model=ct.model, field=k, pattern=None, pattern_type=ptype, convention_set=nc)
            ncf.save()

def nc_create_naming_convention(convention_name):
    nc = NamingConvention(name=convention_name)
    nc.save()
    nc_sync_naming_convention(nc)
    return nc

def __value_pattern_field(nc, instance, pattern, envt=None):
    res = pattern
    
    ## Environment
    if instance.environments.count() > 0 or envt is not None:
        if envt is None:
            envt = instance.environments.all()[0]
        res = res.replace("%e%", envt.name.lower())
        res = res.replace("%E%", envt.name.upper())
    else:
        res = res.replace("%e%", "noenvironment")
        res = res.replace("%E%", "NOENVIRONMENT")
    
    ## Application
    if instance.instanciates is not None:
        trg = instance.instanciates.implements.application
        res = res.replace("%a1%", trg.alternate_name_1.lower())
        res = res.replace("%A1%", trg.alternate_name_1.upper())
        res = res.replace("%a2%", trg.alternate_name_2.lower())
        res = res.replace("%A2%", trg.alternate_name_2.upper())
        res = res.replace("%a3%", trg.alternate_name_3.lower())
        res = res.replace("%A3%", trg.alternate_name_3.upper())
        res = res.replace("%a%", trg.name.lower())
        res = res.replace("%A%", trg.name.upper())
    else:
        res = res.replace("%a1%", "noapplication")
        res = res.replace("%A1%", "NOAPPLICATION")
        res = res.replace("%a2%", "noapplication")
        res = res.replace("%A2%", "NOAPPLICATION")
        res = res.replace("%a3%", "noapplication")
        res = res.replace("%A3%", "NOAPPLICATION")
        res = res.replace("%a", "noapplication")
        res = res.replace("%A", "NOAPPLICATION")
    
    ## Project
    if instance.instanciates is not None and instance.instanciates.implements.application.project is not None:
        trg = instance.instanciates.implements.application.project
        res = res.replace("%p1%", trg.alternate_name_1.lower())
        res = res.replace("%P1%", trg.alternate_name_1.upper())
        res = res.replace("%p2%", trg.alternate_name_2.lower())
        res = res.replace("%P2%", trg.alternate_name_2.upper())
        res = res.replace("%p3%", trg.alternate_name_3.lower())
        res = res.replace("%P3%", trg.alternate_name_3.upper())
        res = res.replace("%p%", trg.name.lower())
        res = res.replace("%P%", trg.name.upper())
    else:
        res = res.replace("%p1%", "noproject")
        res = res.replace("%P1%", "NOPROJECT")
        res = res.replace("%p2%", "noproject")
        res = res.replace("%P2%", "NOPROJECT")
        res = res.replace("%p3%", "noproject")
        res = res.replace("%P3%", "NOPROJECT")
        res = res.replace("%p%", "noproject")
        res = res.replace("%P%", "NOPROJECT")
    
    ## Date (Japanese format)
    d = datetime.datetime.now().strftime('%Y%m%d')
    res = res.replace("%d%", d)
    
    ## Counter
    if "%ce%" in res:
        if envt is None:
            raise MageError('a counter within an environment scope can only be used if the instance is associated to an environment')
        c = NamingConventionCounter.objects.get_or_create(scope_type="environment", scope_param_1=envt.id)[0]
        c.val = c.val + 1    
        c.save()
        
        res = res.replace("%ce%", str(c.val))
    
    if "%cp%" in res:
        if envt is None or envt.project is None:
            raise MageError('a counter within a project scope can only be used if the instance is associated to an environment belonging to a project')
        c = NamingConventionCounter.objects.get_or_create(scope_type="project", scope_param_1=envt.project_id)[0]
        c.val = c.val + 1    
        c.save()
        
        res = res.replace("%cp%", str(c.val))
        
    if "%cg%" in res:        
        c = NamingConventionCounter.objects.get_or_create(scope_type="global", scope_param_1=None)[0]
        c.val = c.val + 1    
        c.save()
        
        res = res.replace("%cg%", str(c.val))
        
    if "%cem%" in res:
        if envt is None:
            raise MageError('a counter within an environment scope can only be used if the instance is associated to an environment')
        c = NamingConventionCounter.objects.get_or_create(scope_type="environment_", scope_param_1=envt.id, scope_param_2 = instance.model_id)[0]
        
        c.val = c.val + 1    
        c.save()
        
        res = res.replace("%cem%", str(c.val))
        
    ## Done
    return res

def __value_instance(nc, instance, envt = None, force=False):
    for ncf in nc.fields.filter(pattern__isnull = False,model= instance.model.model, pattern_type = 'P'):
        if instance.__dict__[ncf.field] is None or force:            
            instance.__dict__[ncf.field] = __value_pattern_field(nc, instance, ncf.pattern, envt)

NamingConvention.value_pattern_field = __value_pattern_field
NamingConvention.value_instance = __value_instance
