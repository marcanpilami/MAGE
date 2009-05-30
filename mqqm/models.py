# coding: utf-8


## MAGE imports
from MAGE.ref.models import Component
from MAGE.ref.admin import ComponentAdmin

## Dango imports
from django.db import models
from django.contrib import admin


###########################################################
## MQ Series
###########################################################

  
  
#########################
## QM      
#########################
class QueueManager(Component):
    port = models.IntegerField(max_length=6)
    adminChannel = models.CharField(max_length=100, verbose_name='Canal admin')
    
    parents = {'serveur': 'Server'}
    
    class Meta:
        verbose_name = u'Gestionnaire de files'
        verbose_name_plural = u'Gestionnaires de files'
        
    detail_template = 'mqqm_pda_details.html'

class QueueManagerAdmin(ComponentAdmin):
    ordering = ('instance_name',)
    list_display = ('instance_name', 'port', 'adminChannel',)
    search_fields = ('instance_name',)
    fieldsets = [
        ('Informations connexion',              {'fields': ['instance_name', 'port', 'adminChannel']}),
        ('Liens avec les autres composants',    {'fields': ['dependsOn', 'connectedTo']}),
        ('Environnements',                      {'fields': ['environments',]}),
    ]
    
    

#########################
## Params      
#########################
class QueueManagerParams(Component):
    def _getQM(self):
        return self.dependsOn.get(model__model='queuemanager').leaf
    qm = property(_getQM)
    def __unicode__(self):
        return "Params %s sur %s" %(self.class_name, self.qm.instance_name)
    
    class Meta:
        verbose_name = u'Paramétrage MQ Series'
        verbose_name_plural = u'Paramétrages MQ Series'
    
class QueueManagerParamsAdmin(ComponentAdmin):
    list_display = ('qm', 'class_name',)
    search_fields = ('dependsOn__class_name', 'dependsOn__instance_name',)
    verbose_name = ('Réside sur',)



#########################
## Registrations      
#########################    
admin.site.register(QueueManager, QueueManagerAdmin)
admin.site.register(QueueManagerParams, QueueManagerParamsAdmin)
