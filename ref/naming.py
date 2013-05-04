'''
Created on 23 mars 2013

@author: Marc-Antoine
'''

import datetime

from django.contrib.contenttypes.models import ContentType

from ref.models import NamingConvention, NamingConventionField, ComponentInstance, \
    NamingConventionCounter, ComponentImplementationClass, Environment
from django.db.models.fields.related import ManyToManyField, ForeignKey
from MAGE.exceptions import MageError
from ref.mcl import parser
from django.forms.fields import BooleanField

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
            if fn in ('dependsOn', 'model', 'pedestals_ci2do', 'statues_ci2do', 'environments', 'configurations', 'subscribers', 'deleted', 'backupitem'):
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
            elif isinstance(field, BooleanField):
                ptype = 'TF'
                
            overwrite_copy = False
            if fn == 'name' or fn.find('password') >= 0:
                overwrite_copy = True
                
            ncf = NamingConventionField(model=ct.model, field=fn, pattern=None, pattern_type=ptype, convention_set=nc, overwrite_copy=overwrite_copy)
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
        elif isinstance(envt, unicode):
            envt = Environment.objects.get(name=envt)
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
        c = NamingConventionCounter.objects.get_or_create(scope_type="environment_", scope_param_1=envt.id, scope_param_2=instance.model_id)[0]
        
        c.val = c.val + 1    
        c.save()
        
        res = res.replace("%cem%", str(c.val))
        
    ## Done
    return res

def __value_bool_field(nc, instance, pattern, envt=None):
    if pattern is None or pattern == 'False' or pattern == 'false':
        return False
    else:
        return True

def __value_instance(nc, instance, envt_name=None, force=False, respect_overwrite=True, create_missing_links=True, force_envt=True):
    ## Environment: take parameter, or what is already defined in the instance, or nothing.
    e = None
    if envt_name is not None:
        e = Environment.objects.get(name__iexact=envt_name)
        if instance.environments.count() == 0 or force_envt:
            instance.environments.add(e)
            envt_name = e.name
    elif instance.environments.count() > 0:
        e = instance.environments.all()[0]
        envt_name = e.name
            
    ## CIC
    cic = nc.fields.filter(pattern__isnull=False, model=instance.model.model, pattern_type='CIC')
    if cic.count() == 1 and (instance.instanciates is not None or force):
        cic = ComponentImplementationClass.objects.get(name=cic)
        instance.instanciates = cic
    
    ## Basic fields: Patterns, TrueFalse
    for ncf in nc.fields.filter(pattern__isnull=False, model=instance.model.model, pattern_type='P'):
        if instance.__dict__[ncf.field] is None or force:            
            instance.__dict__[ncf.field] = __value_pattern_field(nc, instance, ncf.pattern, envt_name)
    
    for ncf in nc.fields.filter(pattern__isnull=False, model=instance.model.model, pattern_type='TF'):
        if instance.__dict__[ncf.field] is None or force:            
            instance.__dict__[ncf.field] = __value_bool_field(nc, instance, ncf.pattern, envt_name)

    ## Relationships 1-1
    for ncf in nc.fields.filter(pattern__isnull=False, model=instance.model.model, pattern_type='MCL1'):
        r = parser.get_components(ncf.pattern)
        if len(r) == 0:
            if not create_missing_links:
                raise MageError('the default query %s has not returned any result - one unique result is required' % ncf.pattern)
            try:
                ## Get class of the relationship
                parents = instance.parents
                type = None
                if parents.has_key(ncf.field):
                    type = parents[ncf.field]['model']
                    type = ContentType.objects.get(model__iexact=type).model_class()
                else:
                    f = instance._meta.get_field_by_name(ncf.field)
                    type = f.model
                
                ## Create empty instance and apply conventions
                c = type()
                nc.value_instance(c, envt_name, force, create_missing_links, False)
                c.save()
                
            except Exception, e:
                raise MageError('cannot create a component instance corresponding to query %s - error is %s' % (ncf.pattern, e))
        if len(r) > 1:
            raise MageError('the default query %s has returned more than one result - one unique result is required' % ncf.pattern)
        
        r = r[0]
        instance.__dict__[ncf.field] = r
    
NamingConvention.value_pattern_field = __value_pattern_field
NamingConvention.value_instance = __value_instance
