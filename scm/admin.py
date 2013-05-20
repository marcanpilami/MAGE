# coding: utf-8

from ref import admin
from scm.models import BackupRestoreMethod, InstallationMethod, BackupSet


class BackupRestoreMethodAdmin(admin.ModelAdmin):
    list_display = ('apply_to', 'target',)
    ordering = ('apply_to', 'target',)
    list_filter = ('apply_to', 'target',)
    
    def has_delete_permission(self, request, obj=None):
        return False
    def get_actions(self, request):
        actions = super(BackupRestoreMethodAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
admin.site.register(BackupRestoreMethod, BackupRestoreMethodAdmin)

class InstallationMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'halts_service', 'available')
    ordering = ('name',)
    list_filter = ('available',)
    filter_horizontal = ('method_compatible_with',)
    
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

admin.site.register(BackupSet, BackupSetAdmin)