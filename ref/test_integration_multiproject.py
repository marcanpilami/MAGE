from django.contrib.auth.models import User

from ref.models import Project
#from ref.demo_items import utility_create_logical, utility_create_meta, utility_create_test_instances
from ref.models.description import clear_classes_cache

from scm.demo_items import create_test_is

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from scm.views import delivery, delivery_list
# from unittest import TestCase

class TestIntegrationMultiproject(TestCase):

    def create_user(self, username, password, is_superuser=False):
        user = User.objects.create_user(username=username, email=None, password=password)
        user.is_superuser = is_superuser
        user.save()

    def setUp(self):
        self.installableSets = create_test_is()
        clear_classes_cache()

        self.project = 'SUPER-PROJECT'

        self.rootUsername = 'root'
        self.rootPassword = 'password'

        self.create_user(self.rootUsername, self.rootPassword, True)

        self.client = Client()

    def test_view_ref_backuped(self):
        self.client.login(username=self.rootUsername, password=self.rootPassword)
        response = self.client.get(reverse('ref:backuped', args=[self.project]))

        if response.context['cis'] is not None:
            for prj in Project.objects.filter(environment__component_instances__id__in=(ci.id for ci in response.context['cis']), name=self.project):
                self.assertEquals(prj.name, self.project)