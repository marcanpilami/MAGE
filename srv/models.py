# coding: utf-8

###########################################################
## Server
###########################################################

from django.db import models
from MAGE.ref.models import Component
from django.contrib import admin

class Server(Component):
    OS_CHOICES = (
                  ('Windows 2003', 'Windows 2003'),
                  ('Windows 2008', 'Windows 2008'),
                  ('AIX 5.3', 'AIX 5.3'),
                  ('Linux', 'Linux'),
                  )
    os          = models.CharField(max_length=30, choices=OS_CHOICES, verbose_name='OS ')
    comment     = models.CharField(max_length=200, blank=True, null=True, verbose_name='Commentaire')
    ip          = models.IPAddressField(verbose_name='IP ')
    
    def __unicode__(self):
        return "Serveur (%s) %s " %(self.os, self.instance_name)



class ServerAdmin(admin.ModelAdmin):
    ordering = ('instance_name',)
    list_display = ('instance_name', 'comment',)
    fieldsets = [
        ('Informations génériques',  {'fields': ['connectedTo', 'dependsOn']}),
        ('Spécifique Serveur',       {'fields': ['instance_name', 'comment', 'ip', 'os']}),
    ]
admin.site.register(Server, ServerAdmin)