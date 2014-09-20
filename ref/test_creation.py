# coding: utf-8
from django.test import TestCase
from ref.demo_items import utility_create_meta
from ref.models.models import ImplementationDescription, Environment, \
    EnvironmentType
from ref.conventions import value_instance_fields

class Creation(TestCase):
    def setUp(self):
        utility_create_meta()

        et1 = EnvironmentType(name='development', description="for developers. No admin except for middlewares.", short_name='DEV', chronological_order=1, default_show_sensitive_data=True)
        et1.save()

        self.e1 = Environment(name='DEV1', description='DEV1', typology=et1)
        self.e1.save()

        self.i1_1 = ImplementationDescription.class_for_name('osserver')(dns='server1.marsu.net', admin_login='test admin')

        self.i2_1 = ImplementationDescription.class_for_name('oracleinstance')(sid='TEST1', admin_login='admin', admin_password='password', server=self.i1_1)

        self.i3_1 = ImplementationDescription.class_for_name('oracleschema')(instance=self.i2_1, _env=self.e1)


    def test_name(self):
        # User%E%%cem%
        value_instance_fields(self.i3_1._instance, force = True)

        self.assertEqual("UserDEV101s1", self.i3_1.name)

