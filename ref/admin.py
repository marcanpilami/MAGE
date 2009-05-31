# coding: UTF-8

"""
    Admin base class for all components

    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""


## Django imports
from django.contrib import admin

## MAGE imports
from models import Component


class ComponentAdmin(admin.ModelAdmin):
    """
        Base admin class for components. It filters 'dependsOn' fields so that the admin will 
        only display relevant components and not every single last one of them, and it provides
        default display behaviour.
        
        @note: This class is NOT meant to be directly used with the Component model, but only with
        models inheriting from Component
    """
    def formfield_for_dbfield(self, db_field, **kwargs):
        ## Find the model that this class admins
        model = [ k for k,v in admin.site._registry.iteritems() if v==self][0]

        ## Superseed the fields as defined in the class
        if model.parents and db_field.name == 'dependsOn':
            kwargs['queryset'] = Component.objects.filter(model__model__in=[u.lower() for u in model.parents.itervalues()])
        return super(ComponentAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    ## Default values for the various admin options. Should usually be at least partially overloaded
    fieldsets_generic = [ ('Informations génériques',  {'fields': ['instance_name', 'class_name', 'environments', 'dependsOn', 'connectedTo']}),]
    fieldsets_generic_no_instance = [ ('Informations génériques',  {'fields': ['class_name', 'environments', 'dependsOn', 'connectedTo']}),]
    fieldsets_generic_no_class = [ ('Informations génériques',  {'fields': ['instance_name', 'environments', 'dependsOn', 'connectedTo']}),]
    fieldsets = fieldsets_generic
    filter_horizontal = ('connectedTo', 'dependsOn', 'environments')
    ordering = ('instance_name','class_name')
    search_fields = ('instance_name','class_name', 'dependsOn__instance_name', 'dependsOn__class_name',)
    list_filter = ['environments',]
