# coding: utf-8

"""
    MAGE backup sample backup module admin file.
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Django imports
from django.contrib import admin

## MAGE imports
from MAGE.sav.models import BackupGroup, GroupComponentAssociation, BackupSet


class AssocInline(admin.TabularInline):
    model = GroupComponentAssociation
    extra = 10


class BackupGroupAdmin(admin.ModelAdmin):
    inlines = [AssocInline,]

class BackupSetAdmin(admin.ModelAdmin):
    #filter_horizontal = ['acts_on',]
    fieldsets = [
        ('Identification',  {'fields': ['name', 'ticket', 'erased_on']}),
        ('Concerne',        {'fields': ['acts_on',]}),     
        ('Divers',          {'fields': ['comment']}),
    ]
    

admin.site.register(BackupSet, BackupSetAdmin)
admin.site.register(BackupGroup, BackupGroupAdmin)