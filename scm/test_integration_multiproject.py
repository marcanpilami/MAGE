from django.contrib.auth.models import User

from ref.models import Project
#from ref.demo_items import utility_create_logical, utility_create_meta, utility_create_test_instances
from ref.models.description import clear_classes_cache

from scm.demo_items import create_test_is

from django.test import Client
from django.test import TestCase
from django.urls import reverse

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

    def test_view_scm_lc_versions_per_environment(self):
        self.client.login(username=self.rootUsername, password=self.rootPassword)
        response = self.client.get(reverse('scm:lc_installs_envts', args=[self.project]))

        if len(response.context['res']):
            for lc, envt_dic in response.context['res'].items:
                for prj in Project.objects.filter(applications__logicalcomponent__id=lc.id, name=self.project):
                    self.assertEquals(prj.name, self.project)

                for envt in envt_dic.items:
                    for prj in Project.objects.filter(environment__id=envt.id, name=self.project):
                        self.assertEquals(prj.name, self.project)


        for envt in response.context['envts']:
            for prj in Project.objects.filter(environment__id=envt.id, name=self.project):
                self.assertEquals(prj.name, self.project)


    def test_view_scm_delivery_list(self):
        self.client.login(username=self.rootUsername, password=self.rootPassword)
        response = self.client.get(reverse('scm:deliveries', args=[self.project]))

        # Trivial test
        self.assertEqual(response.context['project'], self.project)

        if response.context['deliveries'] is not None:
            for prj in Project.objects.filter(applications__logicalcomponent__versions__installed_by__belongs_to_set__id__in=(delivery.id for delivery in response.context['deliveries'])):
                self.assertEquals(prj.name, self.project)

        if response.context['lis'] is not None:
            for prj in Project.objects.filter(applications__logicalcomponent__id__in=(logical_component.id for logical_component in response.context['lis'])):
                self.assertEquals(prj.name, self.project)

    def test_view_scm_delivery_detail(self):
        self.client.login(username=self.rootUsername, password=self.rootPassword)
        response = self.client.get(reverse('scm:delivery_detail', kwargs={'project':self.project, 'iset_id':self.installableSets[0].id}))

        # Trivial test
        self.assertEqual(response.context['project'], self.project)

        if response.context['installs']:
            for prj in Project.objects.filter(name=self.project, environment__id__in=(env.id for env in response.context['installs'])):
                self.assertEquals(prj.name, self.project)

        delivery = response.context['delivery']
        if delivery is not None:
            for prj in Project.objects.filter(applications__logicalcomponent__versions__installed_by__belongs_to_set__id=delivery.id):
                self.assertEquals(prj.name, self.project)

        if response.context['envts']:
            for prj in Project.objects.filter(name=self.project, environment__id__in=(env.id for env in response.context['envts'])):
                self.assertEquals(prj.name, self.project)