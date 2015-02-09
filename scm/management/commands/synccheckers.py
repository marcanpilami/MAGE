# coding: utf-8

# Python imports    

# Django imports
from django.core.management.base import BaseCommand, CommandError
from django.db.transaction import atomic

# MAGE imports
from scm.models import PackageChecker, PackageCheckerBaseImpl
import importlib


#@atomic
class Command(BaseCommand):
    args = '<>'
    help = 'Will check all installed applications for delivery checkers and install them'

    def __init__(self):
        super(Command, self).__init__()
        self.this_launch = []

    def register(self, checker):
        if not issubclass(checker, PackageCheckerBaseImpl):
            raise Exception('a checker must be a subclass of PackageCheckerBaseImpl (' + checker.__name__ + ')')
        print u'registering checker named ' + checker.__name__
        pc = PackageChecker.objects.get_or_create(module=checker.__module__ , name=checker.__name__)
        pc[0].description = checker.description if checker.description else checker.__name__
        pc[0].save()
        self.this_launch.append(pc[0])

    def end_sync(self):
        for pc in PackageChecker.objects.all():
            if not pc in self.this_launch:
                print u'removing checker named ' + pc.name
                pc.delete()

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError('this command takes no parameters')

        ## Load all checkers
        from MAGE.settings import INSTALLED_APPS
        for app in [ i for i in INSTALLED_APPS if not i.startswith('django.')]:
            try:
                module = importlib.import_module(app + '.checkers')
                for value in module.__dict__.values():
                    try:
                        if value.__class__ is type and issubclass(value, PackageCheckerBaseImpl):
                            self.register(value)
                    except AttributeError:
                        continue
            except ImportError:
                continue
        self.end_sync()
