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
    ComponentImplementationClass, Convention, ConventionField, ConventionCounter, ExtendedParameter, \
    EnvironmentType, ImplementationFieldDescription, ImplementationDescription, \
    ImplementationRelationDescription, ImplementationRelationType, \
    ImplementationComputedFieldDescription, ComponentInstanceField, \
    ComponentInstanceRelation
from ref.conventions import nc_sync_naming_convention
from ref.models.parameters import MageParam


################################################################################
## Create admin site object
################################################################################

site = AdminSite()
site.login_template = 'login.html'
#site.logout_template = 'MAGE'
site.register(Group, GroupAdmin)
site.register(User, UserAdmin)


################################################################################
## Parameters
################################################################################

class MageParamAdmin(ModelAdmin):
    list_display = ['app', 'key', 'value', 'model', 'axis1', 'description',]
    search_fields = ['app', 'key', 'value', 'axis1', ]
    list_filter = ['app', ]#'model',]

site.register(MageParam, MageParamAdmin)

################################################################################
## No-frills admins
################################################################################

site.register(SLA)

class EnvironmentAdmin(ModelAdmin):
    fields = ['typology', 'name', 'description', 'project', 'buildDate', 'destructionDate', 'manager', 'template_only', 'active', 'managed', 'show_sensitive_data' ]
    list_display = ('name', 'description', 'template_only', 'managed', 'show_sensitive_data')
    ordering = ('name',)
    readonly_fields = ('buildDate',)
    list_filter = ['template_only', 'managed', 'typology']
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
    list_display = ('name', 'description', 'application', 'ref1', 'ref2', 'ref3')
    ordering = ('application', 'name')
    list_filter = ('application', 'active', 'scm_trackable')
site.register(LogicalComponent, LogicalComponentAdmin)

class ApplicationAdmin(ModelAdmin):
    list_display = ('name', 'description', 'project', 'alternate_name_1')
    ordering = ('name',)
    list_filter = ('project',)
site.register(Application, ApplicationAdmin)

class ProjectAdmin(ModelAdmin):
    list_display = ('name', 'description', 'alternate_name_1', 'alternate_name_2', 'alternate_name_3')
    ordering = ('name',)
site.register(Project, ProjectAdmin)


################################################################################
## CIC
################################################################################

class CICAdmin(ModelAdmin):
    list_display = ('name', 'implements', 'technical_description', 'description')
    list_filter = ('implements__application', 'implements')

site.register(ComponentImplementationClass, CICAdmin)

site.register(ImplementationRelationType)

class ImplementationFieldDescriptionInline(TabularInline):
    model = ImplementationFieldDescription
    extra = 3
    can_delete = True
    fields = ['name', 'datatype', 'default', 'label', 'sensitive' ]

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

class ComponentInstanceFieldAdmin(TabularInline):
    model = ComponentInstanceField
    fields = ['field', 'value', ]

class ComponentInstanceRelationAdmin(TabularInline):
    model = ComponentInstanceRelation
    fields = ['field', 'target', ]
    fk_name = "source"

class ComponentInstanceAdmin(ModelAdmin):
    list_display = ['__unicode__', 'implementation', 'instanciates' ]
    list_filter = ('implementation', 'environments', 'implementation__tag', 'instanciates')
    filter_horizontal = ('environments',)
    inlines = [ComponentInstanceFieldAdmin, ComponentInstanceRelationAdmin, ExtendedParameterInline, ]

site.register(ComponentInstance, ComponentInstanceAdmin)
