# coding: utf-8

import datetime

from django.contrib.contenttypes.models import ContentType

from ref.models import Convention, ConventionField, ComponentInstance, ConventionCounter, ComponentImplementationClass, Environment
from django.db.models.fields.related import ManyToManyField, ForeignKey
from MAGE.exceptions import MageError
from ref.mcl import parser
from django.forms.fields import BooleanField

def nc_sync_naming_convention(nc, model_name_list=None):
    defaults = __get_app_default()
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
            if fn in ('dependsOn', 'model', 'pedestals_ci2do', 'statues_ci2do', 'environments', 'configurations', 'subscribers', 'deleted', 'backupitem', 'parameters'):
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
            
            default = None
            if defaults.has_key(ct.model) and defaults[ct.model].has_key(fn):
                default = defaults[ct.model][fn]
                
            ncf = ConventionField(model=ct.model, field=fn, pattern=default, pattern_type=ptype, convention_set=nc, overwrite_copy=overwrite_copy)
            ncf.save()
            
        # Loop on dependsOn elements so as to create an empty convention for each
        for k, v in ct.model_class().parents.items():
            # Already exists ?
            if nc.fields.filter(field=k, model=ct.model).exists():
                continue
            
            # Create the convention
            ptype = 'MCL0'
            f_card = v.get('cardinality') or 1
            if f_card == 1:
                ptype = 'MCL1'

            default = None
            if defaults.has_key(ct.model) and defaults[ct.model].has_key(k):
                default = defaults[ct.model][k]
                
            ncf = ConventionField(model=ct.model, field=k, pattern=default, pattern_type=ptype, convention_set=nc)
            ncf.save()

def nc_create_naming_convention(convention_name):
    nc = Convention(name=convention_name)
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
        res = res.replace("%E~%", envt.name.capitalize())
    else:
        res = res.replace("%e%", "noenvironment")
        res = res.replace("%E%", "NOENVIRONMENT")
        res = res.replace("%E~%", "NoEnvironment")
    
    ## Application
    if instance.instanciates is not None:
        trg = instance.instanciates.implements.application
        res = res.replace("%a1%", trg.alternate_name_1.lower() if trg.alternate_name_1 else 'noname')
        res = res.replace("%A1%", trg.alternate_name_1.upper() if trg.alternate_name_1 else 'NONAME')
        res = res.replace("%A1~%", trg.alternate_name_1.capitalize() if trg.alternate_name_1 else 'NoName')
        res = res.replace("%a2%", trg.alternate_name_2.lower() if trg.alternate_name_2 else 'noname')
        res = res.replace("%A2%", trg.alternate_name_2.upper() if trg.alternate_name_2 else 'NONAME')
        res = res.replace("%A2~%", trg.alternate_name_2.capitalize() if trg.alternate_name_2 else 'NoName')
        res = res.replace("%a3%", trg.alternate_name_3.lower() if trg.alternate_name_3 else 'noname')
        res = res.replace("%A3%", trg.alternate_name_3.upper() if trg.alternate_name_3 else 'NONAME')
        res = res.replace("%A3~%", trg.alternate_name_3.capitalize() if trg.alternate_name_3 else 'NoName')
        res = res.replace("%a%", trg.name.lower())
        res = res.replace("%A%", trg.name.upper())
        res = res.replace("%A~%", trg.name.capitalize())
    else:
        res = res.replace("%a1%", "noapplication")
        res = res.replace("%A1%", "NOAPPLICATION")
        res = res.replace("%A1~%", "NoApplication")
        res = res.replace("%a2%", "noapplication")
        res = res.replace("%A2%", "NOAPPLICATION")
        res = res.replace("%A2~%", "NoApplication")
        res = res.replace("%a3%", "noapplication")
        res = res.replace("%A3%", "NOAPPLICATION")
        res = res.replace("%A3~%", "NoApplication")
        res = res.replace("%a", "noapplication")
        res = res.replace("%A", "NOAPPLICATION")
        res = res.replace("%A~%", "NoApplication")
    
    ## Project
    if (instance.instanciates is not None and instance.instanciates.implements.application.project is not None) or (instance.environments.filter(project__isnull=False).count() > 0):
        if instance.instanciates is not None and instance.instanciates.implements.application.project is not None:
            trg = instance.instanciates.implements.application.project
        else:
            trg = instance.environments.filter(project__isnull=False).all()[0].project
        res = res.replace("%p1%", trg.alternate_name_1.lower() if trg.alternate_name_1 else 'noname')
        res = res.replace("%P1%", trg.alternate_name_1.upper() if trg.alternate_name_1 else 'NONAME')
        res = res.replace("%P1~%", trg.alternate_name_1.capitalize() if trg.alternate_name_1 else 'NoName')
        res = res.replace("%p2%", trg.alternate_name_2.lower() if trg.alternate_name_2 else 'noname')
        res = res.replace("%P2%", trg.alternate_name_2.upper() if trg.alternate_name_2 else 'NONAME')
        res = res.replace("%P2~%", trg.alternate_name_2.capitalize() if trg.alternate_name_2 else 'NoName')
        res = res.replace("%p3%", trg.alternate_name_3.lower() if trg.alternate_name_3 else 'noname')
        res = res.replace("%P3%", trg.alternate_name_3.upper() if trg.alternate_name_3 else 'NONAME')
        res = res.replace("%P3~%", trg.alternate_name_3.capitalize() if trg.alternate_name_3 else 'NoName')
        res = res.replace("%p%", trg.name.lower())
        res = res.replace("%P%", trg.name.upper())
        res = res.replace("%P~%", trg.name.capitalize())
    else:
        res = res.replace("%p1%", "noproject")
        res = res.replace("%P1%", "NOPROJECT")
        res = res.replace("%P1~%", "NoProject")
        res = res.replace("%p2%", "noproject")
        res = res.replace("%P2%", "NOPROJECT")
        res = res.replace("%P2~%", "NoProject")
        res = res.replace("%p3%", "noproject")
        res = res.replace("%P3%", "NOPROJECT")
        res = res.replace("%P3~%", "NoProject")
        res = res.replace("%p%", "noproject")
        res = res.replace("%P%", "NOPROJECT")
    
    ## CIC
    if instance.instanciates is not None:
        cic = instance.instanciates
        res = res.replace("%ic1%", cic.ref1 or 'noname')
        res = res.replace("%ic2%", cic.ref2 or 'noname')
        res = res.replace("%ic3%", cic.ref3 or 'noname')
        res = res.replace("%IC1%", cic.ref1.upper() if cic.ref1 else 'NONAME')
        res = res.replace("%IC2%", cic.ref2.upper() if cic.ref2 else 'NONAME')
        res = res.replace("%IC3%", cic.ref3.upper() if cic.ref3 else 'NONAME')
        res = res.replace("%IC1~%", cic.ref1.capitalize() if cic.ref1 else 'NoName')
        res = res.replace("%IC2~%", cic.ref2.capitalize() if cic.ref2 else 'NoName')
        res = res.replace("%IC3~%", cic.ref3.capitalize() if cic.ref3 else 'NoName')
    else:
        res = res.replace("%ic1%", "nocic")
        res = res.replace("%ic2%", "nocic")
        res = res.replace("%ic3%", "nocic")
        res = res.replace("%IC1%", "NOCIC")
        res = res.replace("%IC2%", "NOCIC")
        res = res.replace("%IC3%", "NOCIC")
        res = res.replace("%IC1~%", "NoCic")
        res = res.replace("%IC2~%", "NoCic")
        res = res.replace("%IC3~%", "NoCic")
        
    ## LC
    if instance.instanciates is not None and instance.instanciates.implements is not None:
        lc = instance.instanciates.implements
        res = res.replace("%lc1%", lc.ref1 or 'noname')
        res = res.replace("%lc2%", lc.ref2 or 'noname')
        res = res.replace("%lc3%", lc.ref3 or 'noname')
        res = res.replace("%LC1%", lc.ref1.upper() if lc.ref1 else 'NONAME')
        res = res.replace("%LC2%", lc.ref2.upper() if lc.ref2 else 'NONAME')
        res = res.replace("%LC3%", lc.ref3.upper() if lc.ref3 else 'NONAME')
        res = res.replace("%LC1~%", lc.ref1.capitalize() if lc.ref1 else 'NoName')
        res = res.replace("%LC2~%", lc.ref2.capitalize() if lc.ref2 else 'NoName')
        res = res.replace("%LC3~%", lc.ref3.capitalize() if lc.ref3 else 'NoName')
    else:
        res = res.replace("%lc1%", "nolc")
        res = res.replace("%lc2%", "nolc")
        res = res.replace("%lc3%", "nolc")
        res = res.replace("%LC1%", "NOLC")
        res = res.replace("%LC2%", "NOLC")
        res = res.replace("%LC3%", "NOLC")
        res = res.replace("%LC1~%", "NoLc")
        res = res.replace("%LC2~%", "NoLc")
        res = res.replace("%LC3~%", "NoLc")
        
    ## Date (Japanese format)
    d = datetime.datetime.now().strftime('%Y%m%d')
    res = res.replace("%d%", d)
    
    ## Counter
    if "%ce%" in res or '%ce~%' in res:
        if envt is None:
            raise MageError('a counter within an environment scope can only be used if the instance is associated to an environment')
        c = ConventionCounter.objects.get_or_create(scope_type="environment", scope_param_1=envt.id)[0]
        if "%ce%" in res:
            c.val = c.val + 1    
        c.save()
        res = res.replace("%ce%", str(c.val))
        res = res.replace("%ce~%", str(c.val))
    
    if "%cp%" in res or "%cp~%" in res:
        if envt is None or envt.project is None:
            raise MageError('a counter within a project scope can only be used if the instance is associated to an environment belonging to a project')
        c = ConventionCounter.objects.get_or_create(scope_type="project", scope_param_1=envt.project_id)[0]
        if "%cp%" in res:
            c.val = c.val + 1    
        c.save()
        res = res.replace("%cp%", str(c.val))
        res = res.replace("%cp~%", str(c.val))
        
    if "%cg%" in res or "%cg~%" in res:        
        c = ConventionCounter.objects.get_or_create(scope_type="global", scope_param_1=None)[0]
        if "%cg%" in res:
            c.val = c.val + 1    
        c.save()
        res = res.replace("%cg%", str(c.val))
        res = res.replace("%cg~%", str(c.val))
        
    if "%cem%" in res or "%cem~%" in res:
        if envt is None:
            raise MageError('a counter within an environment scope can only be used if the instance is associated to an environment')
        c = ConventionCounter.objects.get_or_create(scope_type="environment_", scope_param_1=envt.id, scope_param_2=instance.model_id)[0]
        if "%cem%" in res:
            c.val = c.val + 1  
        c.save()        
        res = res.replace("%cem%", str(c.val))
        res = res.replace("%cem~%", str(c.val))
        
    ## Done
    return res

def __value_bool_field(nc, instance, pattern, envt=None):
    if pattern is None or pattern == 'False' or pattern == 'false':
        return False
    else:
        return True

def __value_instance(nc, instance, envt_name=None, force=False, respect_overwrite=False, create_missing_links=True, force_envt=True):
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
    if cic.count() == 1 and (instance.instanciates is None or force):
        cic = ComponentImplementationClass.objects.get(name=cic[0].pattern)
        instance.instanciates = cic
    
    ## Basic fields: Patterns, TrueFalse
    for ncf in nc.fields.filter(pattern__isnull=False, model=instance.model.model, pattern_type='P'):
        if instance.__dict__[ncf.field] is None or force or (respect_overwrite and ncf.overwrite_copy):            
            instance.__dict__[ncf.field] = __value_pattern_field(nc, instance, ncf.pattern, envt_name)
    
    for ncf in nc.fields.filter(pattern__isnull=False, model=instance.model.model, pattern_type='TF'):
        if instance.__dict__[ncf.field] is None or force or (respect_overwrite and ncf.overwrite_copy):            
            instance.__dict__[ncf.field] = __value_bool_field(nc, instance, ncf.pattern, envt_name)

    ## Relationships 1..1 and 0..*
    for ncf in nc.fields.filter(pattern__isnull=False, model=instance.model.model, pattern_type__in=('MCL1', 'MCL0')):
        mcl = __value_pattern_field(nc, instance, ncf.pattern, envt_name)
        
        if ncf.pattern_type == 'MCL1' and getattr(instance, ncf.field) is not None and not (force or (respect_overwrite and ncf.overwrite_copy)):
            continue
        if ncf.pattern_type == 'MCL0' and getattr(instance, ncf.field).count() > 0 and not (force or (respect_overwrite and ncf.overwrite_copy)):
            continue
        
        # Get class of the relationship
        parents = instance.parents
        itype = None
        if parents.has_key(ncf.field):
            itype = parents[ncf.field]['model']
            itype = ContentType.objects.get(model__iexact=itype).model_class()
        else:
            f = instance._meta.get_field_by_name(ncf.field)
            itype = f.model

        # Run query
        r = parser.get_components(mcl, allow_create=create_missing_links, force_type=itype.__name__.lower())
        
        # Tests
        if ncf.pattern_type == 'MCL1':
            if len(r) == 0:
                raise MageError('the default query %s has not returned any result - one unique result is required' % ncf.pattern)
            if len(r) > 1:
                raise MageError('the default query %s has returned more than one result - one unique result is required' % ncf.pattern)
            
        # Set result
        if ncf.pattern_type == 'MCL1':
            setattr(instance, ncf.field, r[0])
        elif ncf.pattern_type == 'MCL0':
            instance.__clearcustomlink__(ncf.field)
            for c in r:
                instance.__addtocustomlink__(c, None, ncf.field)

def __get_default_convention(instance):
    ## Note: EnvironmentType > Project 
    c = None
    for envt in instance.environments.all():
        if envt.project is not None and envt.project.default_convention is not None:
            c = envt.project.default_convention
    
    for envt in instance.environments.all():
        if envt.typology is not None and envt.typology.default_convention is not None:
            c = envt.typology.default_convention
            
    return c

def __get_app_default():
    res = {}
    tmp = {}
    from MAGE.settings import INSTALLED_APPS
    for app in [ i for i in INSTALLED_APPS if not i.startswith('django.')]:
        try:
            tmp = getattr(__import__(app + '.models', fromlist=['convention']), 'convention')
        except:
            continue
        for key, values in tmp.items():
            if res.has_key(key):
                res[key].update(values)
            else:
                res[key] = values
    return res
    
Convention.value_pattern_field = __value_pattern_field
Convention.value_instance = __value_instance
ComponentInstance.default_convention = property(__get_default_convention)

