# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

from ref import admin
from scm.models import BackupRestoreMethod, Delivery, InstallationMethod, BackupSet, \
    PackageChecker,InstallableSet, InstallableItem


class BackupRestoreMethodAdmin(admin.ModelAdmin):
    list_display = ('target', 'method')
    ordering = ('target',)

    def has_delete_permission(self, request, obj=None):
        return False
    def get_actions(self, request):
        actions = super(BackupRestoreMethodAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(BackupRestoreMethod, BackupRestoreMethodAdmin)

class InstallationMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'halts_service', 'available', 'restoration_only')
    ordering = ('name',)
    list_filter = ('available', 'restoration_only')
    filter_horizontal = ('method_compatible_with', 'checkers',)

    def has_delete_permission(self, request, obj=None):
        return False
    def get_actions(self, request):
        actions = super(InstallationMethodAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(InstallationMethod, InstallationMethodAdmin)


class BackupSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_available', 'from_envt')
    list_filter = ('from_envt', 'set_date', 'removed')

    def has_delete_permission(self, request, obj=None):
        return False
    def get_actions(self, request):
        actions = super(BackupSetAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

#admin.site.register(BackupSet, BackupSetAdmin)

class PackageCheckerAdmin(admin.ModelAdmin):
    list_display = ('description', 'module', 'name',)
    readonly_fields = ('module', 'name')

admin.site.register(PackageChecker, PackageCheckerAdmin)

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'description', 'logical_component_name', 'ticket_list', 'set_date')
    list_filter = ['status', 'project', ]

    def logical_component_name(self, obj):
        return obj.set_content.all()[0].what_is_installed.logical_component.name if obj.set_content.all() else 'empty IS'

admin.site.register(Delivery, DeliveryAdmin)

#admin.site.register(InstallableItem, InstallableItemAdmin)
#admin.site.register(BackupItem)
admin.site.register(BackupSet)
