# coding: utf-8



## MAGE imports
from MAGE.ref.models import Component
from MAGE.gph.register import registerGraphOption

## Dango imports
from django.db import models
from django.contrib import admin


###########################################################
## MQ Series
###########################################################

class QueueManager(Component):
    port = models.IntegerField(max_length=6)
    adminChannel = models.CharField(max_length=100, verbose_name='Canal admin')
    
    detail_template = 'mqqm_pda_details.html'

class QueueManagerGraphOptions():
    shape='box'
registerGraphOption(QueueManager, QueueManagerGraphOptions)

class QueueManagerParams(Component):
    def _getQM(self):
        return self.dependsOn.get(model__model='queuemanager').leaf
    qm = property(_getQM)
    def __unicode__(self):
        return "Params %s sur %s" %(self.class_name, self.qm.instance_name)
    
class QueueManagerParamsAdmin(admin.ModelAdmin):
    #ordering = ('qm',)
    list_display = ('qm', 'class_name',)


class QueueManagerAdmin(admin.ModelAdmin):
    ordering = ('instance_name',)
    list_display = ('instance_name', 'port', 'adminChannel',)
    fieldsets = [
        ('Informations génériques',  {'fields': ['environments', 'connectedTo', 'dependsOn']}),
        ('Spécifique MQ Series',     {'fields': ['instance_name', 'port', 'adminChannel']}),
    ]
admin.site.register(QueueManager, QueueManagerAdmin)
admin.site.register(QueueManagerParams, QueueManagerParamsAdmin)