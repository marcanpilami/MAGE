# coding: utf-8

###########################################################
## MQ Series
###########################################################

from django.db import models
from MAGE.ref.models import Composant
from django.contrib import admin

class QueueManager(Composant):
    name = models.CharField(max_length=40, verbose_name='Nom du QM') #, unique=True)
    port = models.IntegerField(max_length=6)
    adminChannel = models.CharField(max_length=100, verbose_name='Canal admin')
    
    class Admin():
        pass
    
    def __unicode__(self):
        return "%s (MQSeries)" %(self.name)


class QueueManagerAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'port', 'adminChannel',)
    fieldsets = [
        ('Informations génériques',  {'fields': ['environments', 'connectedTo', 'dependsOn']}),
        ('Spécifique MQ Series',     {'fields': ['name', 'port', 'adminChannel']}),
    ]
admin.site.register(QueueManager, QueueManagerAdmin)