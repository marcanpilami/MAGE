# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Django imports
from django.contrib.admin import SimpleListFilter, ModelAdmin, TabularInline
from django.contrib.contenttypes.models import ContentType
from django.forms.widgets import Select
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin

## MAGE imports
from ref.models import Project, Environment, LogicalComponent, Application, SLA, ComponentInstance, \
    ComponentImplementationClass, Convention, ConventionField, CI2DO, ConventionCounter, ExtendedParameter, \
    EnvironmentType
from ref.conventions import nc_sync_naming_convention


################################################################################
## Create admin site object
################################################################################

site = AdminSite()
site.login_template = 'login.html'
#site.logout_template = 'MAGE'
site.register(Group, GroupAdmin)
site.register(User, UserAdmin)


################################################################################
## No-frills admins
################################################################################

site.register(Project)
site.register(Application)
site.register(SLA)

class EnvironmentAdmin(ModelAdmin):
    fields = ['typology', 'name', 'description', 'project', 'buildDate', 'destructionDate', 'manager', 'template_only', 'active','managed',]
    list_display = ('name', 'description','template_only', 'managed')
    ordering = ('name',)
    readonly_fields=('buildDate',)
    list_filter = ['template_only', 'managed',]
    search_fields = ('name',)
    
    
    def has_delete_permission(self, request, obj=None):
        return False
    def get_actions(self, request):
        actions = super(EnvironmentAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

site.register(Environment, EnvironmentAdmin)

class EnvironmentTypeAdmin(ModelAdmin):
    list_display = ('name', 'short_name', 'description', 'chronological_order',)
    ordering = ('chronological_order', 'name')
    filter_horizontal = ('implementation_patterns',)

site.register(EnvironmentType, EnvironmentTypeAdmin)


class LogicalComponentAdmin(ModelAdmin):
    list_display = ('name', 'description', 'application','ref1', 'ref2', 'ref3')
    ordering = ('application', 'name')
    list_filter = ('application', 'active','scm_trackable')
site.register(LogicalComponent, LogicalComponentAdmin)


################################################################################
## CIC
################################################################################

class CICAdmin(ModelAdmin):
    list_display = ('name', 'implements', 'python_model_to_use', 'description')
    list_filter = ('implements',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "python_model_to_use":
            kwargs["queryset"] = ContentType.objects.exclude(app_label__in=('ref', 'scm', 'prm', 'auth', 'contenttypes', 'sessions', 'sites', 'messages', 'admin'))
        return super(CICAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    
site.register(ComponentImplementationClass, CICAdmin)


################################################################################
## Naming conventions
################################################################################
    
class ConventionFieldInline(TabularInline):
    model = ConventionField
    extra = 0
    can_delete = False
    fields = ['model', 'field', 'pattern_type', 'overwrite_copy', 'pattern', ]
    readonly_fields = ['model', 'field', 'pattern_type']
    ordering = ['model', 'field']
    template = 'admin/tabular_no_title.html'

class ConventionAdmin(ModelAdmin):
    fields = ['name', ]
    inlines = [ConventionFieldInline, ]
    actions = ['make_refresh_nc', ]
    
    def make_refresh_nc(self, request, queryset):
        for nc in queryset:
            nc_sync_naming_convention(nc)
            self.message_user(request, "%s successfully refreshed." % nc.name)
    make_refresh_nc.short_description = u'actualiser les champs des modèles'

site.register(Convention, ConventionAdmin)

class ConventionCounterAdmin(ModelAdmin):
    list_display = ('scope_type', 'scope_param_1', 'scope_param_2', 'val')
    
site.register(ConventionCounter, ConventionCounterAdmin)


################################################################################
## Component instances
################################################################################

class ExtendedParameterInline(TabularInline):
    model = ExtendedParameter
    
class CI2DOFieldInline(TabularInline):
    model = CI2DO
    extra = 5
    can_delete = True
    fields = ['rel_name', 'pedestal', ]
    fk_name = 'statue'
    template = 'admin/tabular_no_title.html'
      
    def formfield_for_dbfield(self, db_field, **kwargs):
        path = kwargs['request'].path
        statue_model_name = path.split('/')[path.split('/').index('admin') + 2]
        statue_model = ContentType.objects.get(model__iexact=statue_model_name).model_class()
        
        if db_field.name == "pedestal":
            potential_link_models = [v['model'].lower() for v in statue_model.parents.values()]
            kwargs["queryset"] = ComponentInstance.objects.filter(model__model__in=potential_link_models)
            
        ## Superseed the fields as defined in the class
        if db_field.name == 'rel_name':
            kwargs['widget'] = Select(choices=[('', '---------'), ] + [ (i, i) for i in statue_model.parents.keys()])

        
        return super(CI2DOFieldInline, self).formfield_for_dbfield(db_field, **kwargs)

    
class CICFilter(SimpleListFilter):
    title = u'implémentation de'
    parameter_name = 'impl'

    def lookups(self, request, model_admin):
        model_name = request.path.split('/')[3]
        cics = ComponentImplementationClass.objects.filter(python_model_to_use__model__iexact=model_name)
        res = ()
        for cic in cics:
            res += ((cic.id, cic.__unicode__()),)
        return res

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(instanciates_id=self.value())
        else:
            return queryset

class ComponentInstanceAdmin(ModelAdmin):
    """
        Base admin class for components. It filters 'dependsOn' fields so that the admin will 
        only display relevant components and not every single last one of them, and it provides
        default display behaviour.
        
        @note: This class is NOT meant to be directly used with the Component model, but only with
        models inheriting from Component
    """
    def formfield_for_dbfield(self, db_field, **kwargs):
        ## Find the model that this class admins
        model = [ k for k, v in site._registry.iteritems() if v == self][0]

        ## Superseed the fields as defined in the class
        if db_field.name == 'dependsOn' and hasattr(model, 'parents'):
            kwargs['queryset'] = ComponentInstance.objects.filter(model__model__in=[u.lower() for u in model.parents.itervalues()])
        elif db_field.name == 'dependsOn' and not hasattr(model, 'parents'):
            kwargs['queryset'] = ComponentInstance.objects.none()
            
        if db_field.name == 'instanciates':
            kwargs['queryset'] = ComponentImplementationClass.objects.filter(python_model_to_use__model__iexact=model.__name__)
            
        if db_field.name == 'service_name_to_use':
            print kwargs
            
        return super(ComponentInstanceAdmin, self).formfield_for_dbfield(db_field, **kwargs)


    ## Default values for the various admin options. Should usually be at least partially overloaded
    fieldsets_generic = [ ('Informations génériques', {'fields': ['name', 'instanciates', 'environments', 'connectedTo', 'include_in_envt_backup', 'deleted']}), ]
    fieldsets_generic_no_class = [ ('Informations génériques', {'fields': ['environments', 'connectedTo']}), ]
    fieldsets = fieldsets_generic
    filter_horizontal = ('connectedTo', 'dependsOn', 'environments')
    ordering = ('name',)
    search_fields = ('name', 'dependsOn__name',)
    list_filter = ['environments', CICFilter, 'deleted']
    list_display = ('name', 'instanciates', 'deleted')
    inlines = [CI2DOFieldInline, ExtendedParameterInline, ]
    
    ## Prevent deletion - should be marked ununsed instead
    def has_delete_permission(self, request, obj=None):
        return False
    def get_actions(self, request):
        actions = super(ComponentInstanceAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

