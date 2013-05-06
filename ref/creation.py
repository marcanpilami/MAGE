# coding: utf-8
from ref.models import Environment, ComponentInstance, CI2DO, ExtendedParameter
from ref.mcl import parser

def duplicate_envt(envt_name, new_name, remaps, *components_to_duplicate):
    """ 
    @param envt_name: the name of the environment to duplicate
    @param new_name: name of the new environment. Must not already exist.
    @param remaps: links to objects not in the components_to_duplicate will stay as they are in the source, unless a remap is specified. Dictionary. { (oldid, newid), ... )
    @param components_to_duplicate: list of components to duplicate; If the components are not in the source environement, it is ignored. If the list is empty, every component instance is copied.
    """
    envt = Environment.objects.get(name=envt_name)
    old_envt = Environment.objects.get(name=envt_name)
    
    if components_to_duplicate is None or len(components_to_duplicate) == 0:
        components_to_duplicate = envt.component_instances.all()
    internal_pks = [i.pk for i in components_to_duplicate] 
    already_migrated = {} # key = old PK, value = new instance
    
    ## Duplicate the envt
    envt.id = None
    envt.name = new_name
    envt.save()
    
    ## Duplicate the instances
    for instance in components_to_duplicate:
        old = ComponentInstance.objects.get(pk=instance.pk).leaf
        
        ###############################
        ## First pass: basic fields.
        
        instance = instance.leaf
        instance.pk = None
        instance.id = None ## Inheritance!
        instance.save()
        already_migrated[old.pk] = instance
        
        ## Basics relations
        instance.environments.add(envt)
        instance.instanciates = old.instanciates
        
        ## Extended parameters
        for prm in old.parameters.all():
            p = ExtendedParameter(key=prm.key, value=prm.value, instance=instance)
            p.save()
        
        ###############################
        ## dependsOn
        
        ## Direct relation
        for ci2do in old.pedestals_ci2do.all():
            if ci2do.pedestal.id in internal_pks:
                ## Remap to duplicated element. If not duplicated yet, don't - it will be specified with the reverse relation
                if ci2do.pedestal.id in already_migrated.keys():
                    c = CI2DO(statue=instance, pedestal=already_migrated[ci2do.pedestal.id], rel_name=ci2do.rel_name)
                    c.save()
                else:
                    pass
            else:
                ## This is an external mapping.
                if ci2do.pedestal.id in remaps.keys():
                    ## Remap was asked.
                    remapped_pedestal = ComponentInstance.objects.get(pk=remaps[ci2do.pedestal.id])
                    c = CI2DO(statue=instance, pedestal=remapped_pedestal, rel_name=ci2do.rel_name)
                    c.save()
                else:
                    ## Keep the template relationship
                    c = CI2DO(statue=instance, pedestal=ci2do.pedestal, rel_name=ci2do.rel_name)
                    c.save()
            
        ## Reverse relation
        for ci2do in old.statues_ci2do.all():
            if ci2do.statue.id in internal_pks:
                ## Remap to duplicated element. If not duplicated yet, don't - it will be specified with the direct relation
                if ci2do.statue.id in already_migrated.keys():
                    c = CI2DO(statue=already_migrated[ci2do.statue.id], pedestal=instance, rel_name=ci2do.rel_name)
                    c.save()
                else:
                    pass
            else:
                pass ## External mappings are all done in the direct relation analysis
        
        
        ###############################
        ## connectedTo
        
        # Direct relation
        for cnx in old.connectedTo.all():
            if cnx.pk in internal_pks:
                if cnx.pk in already_migrated.keys():
                    instance.connectedTo.add(already_migrated[cnx.id])
                else:
                    pass # see reverse relation
            else:
                if cnx.id in remaps.keys():
                    instance.connectedTo.add(ComponentInstance.objects.get(pk=remaps[cnx.id]))
                else:
                    instance.connectedTo.add(cnx)
        
        # Reverse: no need, relation is symmetrical.
        
        
        ###############################
        ## Convention
        c = instance.default_convention
        if c is not None:
            c.value_instance(instance, force=False, respect_overwrite=True, create_missing_links=False)
        
        ###############################
        instance.save()
    
    return envt


def create_instance(self, mcl, apply_convention = True, apply_convention_force = False):
    instance = parser.get_components(mcl, True)[0]
    
    if apply_convention:
        c= instance.default_convention
        if c:
            c.value_instance(instance, force = apply_convention_force)
    
    return instance
