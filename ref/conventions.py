# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Django imports
from django.utils.timezone import now

## MAGE imports
from MAGE.exceptions import MageError
from ref.models import ConventionCounter, Environment, ComponentInstanceField
import re
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save
from ref.naming_language import resolve

# Public regex
re_counter_tyev = re.compile("(%cem(~)?(\d+)?)%")
re_counter_type = re.compile("(%cm(~)?(\d+)?)%")
re_counter_envt = re.compile("(%ce(~)?(\d+)?)%")
re_counter_prjt = re.compile("(%cp(~)?(\d+)?)%")
re_counter_glob = re.compile("(%cg(~)?(\d+)?)%")
re_counter_item = re.compile(r"(%ci(~)?(\d+)?([\w_\.]+)%)")
re_navigation = re.compile(r"(%n([\w_\.]+)%)")
re_maths = re.compile(r'^[\d\+\-\*\/\(\)]+$')

def __value_pattern_field(instance, pattern, envt=None, counter_simulation=False):
    """
        @param instance: the component instance. It is not modified here, but used as a reference for environment, cic, ...
        @param pattern: the pattern to value
        @param envt: offers the possibility to overload the environment, or to select a single environment if the instance is inside multiple ones.
        @param counter_simulation: if True, no counters will be ever incremented in the database - but their incremented value will still be used.
    """
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
        res = res.replace("%a%", "noapplication")
        res = res.replace("%A%", "NOAPPLICATION")
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
    d = now().strftime('%Y%m%d')
    res = res.replace("%d%", d)

    ## Counter
    for match in reversed([i for i in re_counter_envt.finditer(res)]):
        if envt is None:
            raise MageError('a counter within an environment scope can only be used if the instance is associated to an environment')
        c = ConventionCounter.objects.get_or_create(scope_project=None, scope_application=None, scope_environment=envt, scope_type=None, scope_instance=None)[0]
        res = __counter(match, res, c, counter_simulation)

    for match in reversed([i for i in re_counter_prjt.finditer(res)]):
        if envt is None or envt.project is None:
            raise MageError('a counter within a project scope can only be used if the instance is associated to an environment belonging to a project')
        c = ConventionCounter.objects.get_or_create(scope_project=envt.project, scope_application=None, scope_environment=None, scope_type=None, scope_instance=None)[0]
        res = __counter(match, res, c, counter_simulation)

    for match in reversed([i for i in re_counter_glob.finditer(res)]):
        c = ConventionCounter.objects.get_or_create(scope_project=None, scope_application=None, scope_environment=None, scope_type=None, scope_instance=None)[0]
        res = __counter(match, res, c, counter_simulation)

    for match in reversed([i for i in re_counter_tyev.finditer(res)]):
        if envt is None:
            raise MageError('a counter within an environment scope can only be used if the instance is associated to an environment')
        c = ConventionCounter.objects.get_or_create(scope_project=None, scope_application=None, scope_environment=envt, scope_type=instance.description, scope_instance=None)[0]
        res = __counter(match, res, c, counter_simulation)

    for match in reversed([i for i in re_counter_type.finditer(res)]):
        if instance.description_id is None:
            raise MageError('a counter within a description scope can only be used if the instance is correctly associated to a description')
        c = ConventionCounter.objects.get_or_create(scope_project=None, scope_application=None, scope_environment=None, scope_type=instance.description, scope_instance=None)[0]
        res = __counter(match, res, c, counter_simulation)

    ## Maths?
    if re_maths.search(res):
        try:
            res = eval(res)
        except:
            pass

    ## Done
    return res

def __counter(match, res, counter, counter_simulation):
    # Only advance sequence if tilde is absent
    val = counter.val
    if not counter_simulation and match.groups()[1] is None:
        counter.val = counter.val + 1
        counter.save()
    if match.groups()[1] is None:
        val = val + 1

    # Padding
    if not match.groups()[2] is None:
        val = format(val, '0' + match.groups()[2])

    return res[0:match.start()] + str(val) + res[match.end():]

def value_instance_graph_fields(instance, force=False):
    """Only values fields depending on another instance. Should be called once the instance relations are set"""
    if not instance.description:
        raise Exception ('cannot value an instance without structure')
    impl = instance.description

    for field in impl.field_set.all():
        if not field.default:
            continue
        existing = ComponentInstanceField.objects.get_or_none(instance_id=instance.id, field_id=field.id)
        new_val = existing.value or field.default

        if field.default and (existing is None or force or existing.value == field.default or re_counter_item.search(existing.value)):
            for match in reversed([i for i in re_counter_item.finditer(new_val)]):
                scope_pivot = resolve(match.groups()[3], instance)
                c = ConventionCounter.objects.get_or_create(scope_project=None, scope_application=None, scope_environment=None, scope_type=instance.description, scope_instance=scope_pivot)[0]
                new_val = __counter(match, new_val, c, False)

        if field.default and (existing is None or not existing.value or force or re_navigation.search(existing.value)):
            for match in reversed([i for i in re_navigation.finditer(new_val)]):
                scope_pivot = resolve(match.groups()[1], instance)
                new_val = new_val[0:match.start()] + str(scope_pivot) + new_val[match.end():]

        ## Maths?
        if re_maths.search(new_val):
            try:
                new_val = eval(new_val)
            except:
                pass

        if not existing is None:
            existing.value = new_val
            existing.save()
        else:
            n = ComponentInstanceField(value=new_val, field=field, instance=instance)
            n.save()

def value_instance_fields(instance, force=False, create_missing_links=True, counter_simulation=False):
    """
        Applies defaults & naming conventions to a component instance. Only deals with user-defined fields.
        Environment, CIC & such should be set BEFORE calling this function.
        @param instance: the component instance to value
        @param force: overwrite a field with a non-None computed value even if the field is not None.
        @param create_missing_links: ? - future use
    """

    if not instance.description:
        raise Exception ('cannot value an instance without structure')
    impl = instance.description

    for field in impl.field_set.all():
        existing = ComponentInstanceField.objects.get_or_none(instance_id=instance.id, field_id=field.id)
        if field.default and (existing is None or force):
            new_val = __value_pattern_field(instance, field.default, counter_simulation=counter_simulation)
        else:
            continue
        if not existing is None:
            existing.value = new_val
            existing.save()
        else:
            n = ComponentInstanceField(value=new_val, field=field, instance=instance)
            n.save()
