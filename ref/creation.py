# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2022 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from ref.models import Environment, ComponentInstance, ExtendedParameter, \
    EnvironmentType
from ref.models.instances import ComponentInstanceField, ComponentInstanceRelation
from ref.conventions import value_instance_fields, value_instance_graph_fields


def duplicate_envt(envt_name, new_name, remaps={}, *components_to_duplicate):
    """ 
    @param envt_name: the name of the environment to duplicate
    @param new_name: name of the new environment. Must not already exist.
    @param remaps: links to objects not in the components_to_duplicate will stay as they are in the source, unless a remap is specified. Dictionary. { (oldid, newid), ... )
    @param components_to_duplicate: list of components to duplicate; If the components are not in the source environement, it is ignored. If the list is empty, every component instance is copied.
    """
    envt = Environment.objects.get(name=envt_name)
    #old_envt = Environment.objects.get(name=envt_name)

    if components_to_duplicate is None or len(components_to_duplicate) == 0:
        components_to_duplicate = envt.component_instances.all()
    components_to_duplicate = sorted(list(components_to_duplicate), key=lambda compo : compo.pk)
    internal_pks = [i.pk for i in components_to_duplicate]
    already_migrated = {} # key = old PK, value = new instance

    ## Duplicate the envt
    envt.id = None
    envt.name = new_name
    envt.template_only = False
    envt.description = "copied from environment %s (%s)" % (envt_name, envt.description)

    ## Try to find the ET
    for et in EnvironmentType.objects.all():
        if et.short_name in new_name:
            envt.typology = et
            break
    else:
        envt.typology = envt.typology # Stupid but...
    envt.save()

    ## Duplicate the instances
    for old in components_to_duplicate:
        if old.deleted:
            continue

        ###############################
        ## First pass: basic fields.

        new_instance = ComponentInstance(instanciates=old.instanciates, description=old.description, include_in_envt_backup=old.include_in_envt_backup, project=old.project)
        new_instance.save()
        new_instance.environments.add(envt)
        already_migrated[old.pk] = new_instance

        for fv in old.field_set.all():
            new_instance.field_set.add(ComponentInstanceField(value=fv.value, field=fv.field), bulk=False)

        ## Relationships
        for fv in old.rel_target_set.all():
            new_target = None
            if fv.target.id in remaps.keys():
                # Should be remapped
                new_target = ComponentInstance.objects.get(pk=remaps[fv.target.id])
            elif fv.target.id in already_migrated.keys():
                # Internal key - remap to copied instance
                new_target = already_migrated[fv.target.id]
            elif not fv.target.id in internal_pks:
                # external, but not remapped -> leave it as it is.
                new_target = fv.target
            if new_target:
                t = ComponentInstanceRelation(source=new_instance, target=new_target, field=fv.field)
                t.save()

        for fv in old.rel_targeted_by_set.all():
            new_source = None
            if fv.source.id in remaps.keys():
                # Should be remapped
                new_source = ComponentInstance.objects.get(pk=remaps[fv.source.id])
            elif fv.source.id in already_migrated.keys():
                # Internal key - remap to copied instance
                new_source = already_migrated[fv.source.id]
            elif not fv.source.id in internal_pks:
                # external, but not remapped -> leave it as it is.
                new_source = fv.source
            if new_source:
                t = ComponentInstanceRelation(source=new_source, target=new_instance, field=fv.field)
                t.save()

        ## Extended parameters
        for prm in old.parameter_set.all():
            p = ExtendedParameter(key=prm.key, value=prm.value, instance=new_instance)
            p.save()


        ###############################
        ## Convention
        if new_instance is not None:
            value_instance_fields(new_instance, force=True)


        ###############################
        new_instance.save()

    ## Apply second step of conventions to instances
    for instance in envt.component_instances.all():
        value_instance_graph_fields(instance)

    return envt
