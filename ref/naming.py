'''
Created on 23 mars 2013

@author: Marc-Antoine
'''

from django.contrib.contenttypes.models import ContentType

from ref.models import NamingConvention, NamingConventionField, ComponentInstance

def nc_sync_naming_convention(nc, model_name_list = None):
    cts = None
    if model_name_list is None or len(model_name_list) == 0:
        cts = ContentType.objects.all()
    else:
        cts = ContentType.objects.filter(model__in = model_name_list)
    
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
            
            # Only true model fields
            if field.auto_created or not field.editable:
                continue
            
            # Already exists ?
            if nc.fields.filter(field=fn).filter(model=ct.model).exists():
                continue
            
            # Create a convetion for the field
            ncf = NamingConventionField(model=ct.model, field=fn, pattern=None, convention_set=nc)
            ncf.save()
            

def nc_create_naming_convention(convention_name):
    nc = NamingConvention(name=convention_name)
    nc.save()
    nc_sync_naming_convention(nc)
    return nc
