# coding: utf-8

# Python imports
from datetime import  timedelta

# Django imports
from django.core.management.base import BaseCommand, CommandError
from django.db.models.aggregates import Count
from django.utils import timezone
from django.db.transaction import atomic

# MAGE imports
from scm.models import BackupSet


@atomic
class Command(BaseCommand):
    args = '<older_than_days>'
    help = 'Purges old archived backupsets from the database. Sets that were used for at least one restoration are left untouched.'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('no parameter specified')
        try:
            days = int(args[0])
        except:
            raise CommandError('parameter should be an integer')
        
        limit = timezone.now() - timedelta(days=days)
        init = BackupSet.objects.filter(removed__isnull=False).count()
        
        # do a loop - SQLite limitation that is only overcome in Django 1.8 - https://code.djangoproject.com/ticket/16426
        for bs in BackupSet.objects.filter(removed__isnull=False, set_date__lte=limit).annotate(installs=Count('installation')).filter(installs=0):
            bs.delete()        
        
        print("%s backupsets purged" %(init - BackupSet.objects.filter(removed__isnull=False).count()))
