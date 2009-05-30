# coding: utf-8

###########################################################
## Informatica folder
###########################################################

#TODO: the IFPC components are not defined yet, those are just here for referential engine debug purposes

from django.db import models
from MAGE.ref.models import *
from django.contrib import admin

class IFPCFolder(Component):
    def _getProject(self):
        return self.dependsOn.get(model__model='ifpcproject').leaf
    ifpc_project = property(_getProject) 
    
    detail_template = 'fif_folder_details.html'
    parents = {'ifpc_project':'IFPCProject'}
    
    def __unicode__(self):
        return u'%s' %(self.class_name) 

    class Meta:
        verbose_name=u"folder Informatica"
        verbose_name_plural = u"folders Informatica"


class IFPCFolderAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'ifpc_project')
    list_filter = ('dependsOn',)
    fieldsets = (
                    (u'Général', 
                        {'fields': ('class_name', 'environments')}
                    ),
                    (u'Connexions',
                        {'fields': ('connectedTo', 'dependsOn')}
                    )
                )
                    
    filter_horizontal = ('connectedTo', 'dependsOn', 'environments')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        print 'iii'
        print db_field
        for (key,value) in kwargs:
            print 'mmm' + key + value
        if db_field.name=='dependsOn':
            kwargs['queryset'] = Component.objects.filter(model__model='ifpcproject')
        return super(IFPCFolderAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        
admin.site.register(IFPCFolder, IFPCFolderAdmin)

class IFPCProject(Component):
    pass