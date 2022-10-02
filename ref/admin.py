# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Django imports
from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin

## MAGE imports
from ref.models import Project, Environment, LogicalComponent, Application, SLA, \
    ComponentImplementationClass, ConventionCounter, ExtendedParameter, \
    EnvironmentType, ImplementationFieldDescription, ImplementationDescription, \
    ImplementationRelationDescription, ImplementationRelationType, \
    ImplementationComputedFieldDescription, ComponentInstanceField, \
    ComponentInstanceRelation
from ref.models.parameters import MageParam
from ref.models.com import Link


################################################################################
## Create admin site object
################################################################################

site = AdminSite()
site.login_template = 'login.html'
site.site_header = "Administration MAGE"
site.site_title = 'MAGE'
site.index_title = None
site.register(Group, GroupAdmin)
site.register(User, UserAdmin)


################################################################################
## Parameters
################################################################################

class MageParamAdmin(ModelAdmin):
    list_display = ['app', 'key', 'value', 'model', 'axis1', 'description', ]
    search_fields = ['app', 'key', 'value', 'axis1', ]
    list_filter = ['app', ]  #'model',]
    readonly_fields = ['default_value', ]

site.register(MageParam, MageParamAdmin)

################################################################################
## No-frills admins
################################################################################

site.register(SLA)

class EnvironmentAdmin(ModelAdmin):
    fields = ['typology', 'name', 'description', 'project', 'buildDate', 'destructionDate', 'manager', 'template_only', 'active', 'managed', 'show_sensitive_data' ]
    list_display = ('name', 'description', 'template_only', 'managed', 'active', 'show_sensitive_data')
    ordering = ('name',)
    readonly_fields = ('buildDate',)
    list_filter = ['project', 'template_only', 'managed', 'typology']
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
    search_fields = ('name', 'short_name')

site.register(EnvironmentType, EnvironmentTypeAdmin)


class LogicalComponentAdmin(ModelAdmin):
    list_display = ('name', 'description', 'application', 'ref1', 'ref2', 'ref3')
    ordering = ('application', 'name')
    list_filter = ('application__project', 'application', 'active', 'scm_trackable')
site.register(LogicalComponent, LogicalComponentAdmin)

class ApplicationAdmin(ModelAdmin):
    list_display = ('name', 'description', 'project', 'alternate_name_1', 'alternate_name_2', 'alternate_name_3')
    ordering = ('name',)
    list_filter = ('project',)
site.register(Application, ApplicationAdmin)

class ProjectAdmin(ModelAdmin):
    list_display = ('name', 'description', 'alternate_name_1', 'alternate_name_2', 'alternate_name_3')
    ordering = ('name',)
site.register(Project, ProjectAdmin)

class LinkAdmin(ModelAdmin):
    list_display = ('url', 'legend')
site.register(Link, LinkAdmin)


################################################################################
## CIC
################################################################################

class CICAdmin(ModelAdmin):
    list_display = ('name', 'implements', 'technical_description', 'description', 'active')
    list_filter = ('active', 'implements__application__project', 'implements__application', 'implements', 'description')

site.register(ComponentImplementationClass, CICAdmin)

class ImplementationRelationTypeAdmin(ModelAdmin):
    list_display = ('name', 'label')
site.register(ImplementationRelationType, ImplementationRelationTypeAdmin)

class ImplementationFieldDescriptionInline(TabularInline):
    model = ImplementationFieldDescription
    extra = 3
    can_delete = True
    fields = ['name', 'datatype', 'default', 'label', 'compulsory', 'sensitive', 'widget_row' ]

class ImplementationRelationDescriptionInline(TabularInline):
    model = ImplementationRelationDescription
    extra = 1
    fk_name = "source"

class ImplementationComputedFieldDescriptionInline(TabularInline):
    model = ImplementationComputedFieldDescription
    extra = 1

class ImplementationDescriptionAdmin(ModelAdmin):
    list_display = ('name', 'description', 'tag')
    list_filter = ('tag',)
    inlines = [ImplementationFieldDescriptionInline, ImplementationRelationDescriptionInline, ImplementationComputedFieldDescriptionInline]

site.register(ImplementationDescription, ImplementationDescriptionAdmin)


################################################################################
## Naming conventions
################################################################################

class ConventionCounterAdmin(ModelAdmin):
    list_filter = ('scope_project', 'scope_application', 'scope_environment', 'scope_type')
    list_display = ('scope_project', 'scope_application', 'scope_environment', 'scope_type', 'scope_instance', 'val')

site.register(ConventionCounter, ConventionCounterAdmin)


################################################################################
## Component instances
################################################################################

class ExtendedParameterInline(TabularInline):
    model = ExtendedParameter

class ComponentInstanceFieldAdmin(TabularInline):
    model = ComponentInstanceField
    fields = ['field', 'value', ]

class ComponentInstanceRelationAdmin(TabularInline):
    model = ComponentInstanceRelation
    fields = ['field', 'target', ]
    fk_name = "source"

class ComponentInstanceAdmin(ModelAdmin):
    list_display = ['__str__', 'description', 'instanciates', 'active' ]
    list_filter = ('project', 'deleted', 'description', 'environments', 'description__tag', 'instanciates')
    filter_horizontal = ('environments',)
    inlines = [ComponentInstanceFieldAdmin, ComponentInstanceRelationAdmin, ExtendedParameterInline, ]

#site.register(ComponentInstance, ComponentInstanceAdmin) 
