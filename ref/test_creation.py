# coding: utf-8
from django.test import TestCase
from ref.demo_items import utility_create_meta
from ref.models.instances import ImplementationDescription, Environment, \
    EnvironmentType, Project, Application
from ref.conventions import value_instance_fields

class Creation(TestCase):
    def setUp(self):
        utility_create_meta()

        p1 = Project(name='SUPER-PROJECT', description='New ERP for FIRM1. A Big Program project.', alternate_name_1='ERP', alternate_name_2='PROJECTCODE')
        p1.save()
        a1 = Application(name='Soft1', description='Super New ERP')
        a1.save()
        a2 = Application(name='Interfaces', description='developments to interface Soft1 with the rest of the FIRM1 systems')
        a2.save()
        p1.applications.add(a1, a2)

        et1 = EnvironmentType(name='development', description="for developers. No admin except for middlewares.", short_name='DEV', chronological_order=1, default_show_sensitive_data=True)
        et1.save()

        self.e1 = Environment(name='DEV1', description='DEV1', typology=et1)
        self.e1.save()
        p1.environment_set.add(self.e1)

        self.i1_1 = ImplementationDescription.class_for_name('osserver')(dns='server1.marsu.net', admin_login='test admin')
        self.i1_2 = ImplementationDescription.class_for_name('osserver')(dns='server2.marsu.net', admin_login='test admin')
        
        self.i2_1 = ImplementationDescription.class_for_name('oracleinstance')(sid='TEST1', admin_login='admin', admin_password='password', server=self.i1_1)


        self.i4_1 = ImplementationDescription.class_for_name('jbossdomain')(name=u'domain études', admin_user='admin', admin_password='pass', \
                base_http_port=8080, base_https_port=8081, web_admin_port=9990, native_admin_port=9999)
        self.i5_1 = ImplementationDescription.class_for_name('jbosshost')(name=u'jbosshost1.marsu.net', domain=self.i4_1, server=self.i1_1)
        self.i6_1 = ImplementationDescription.class_for_name('jbossgroup')(name=u'ErpAsDev1_01', profile='DEV1', \
               dedicated_admin_login='dev1', dedicated_admin_password='dev1', domain=self.i4_1, _env=self.e1)
        self.i6_2 = ImplementationDescription.class_for_name('jbossgroup')(name=u'ErpAsDev1_02', profile='DEV1', \
               dedicated_admin_login='dev1', dedicated_admin_password='dev1', domain=self.i4_1, _env=self.e1)


    def test_counter_type_plus_envt(self):
        # User%E%%cem%
        schema = ImplementationDescription.class_for_name('oracleschema')(instance=self.i2_1, _env=self.e1)
        self.assertEqual("UserDev101s1", schema.name)

    def test_counter_item(self):
        jas = ImplementationDescription.class_for_name('jbossas')(host=self.i1_1, group=self.i6_1 , _env=self.e1)
        self.assertEqual("ErpAsDev1_01_01", jas.name)
        self.assertEqual("10", jas.port_shift)

        # should increment item counter which is on group
        jas = ImplementationDescription.class_for_name('jbossas')(host=self.i1_1, group=self.i6_1 , _env=self.e1)
        self.assertEqual("ErpAsDev1_01_02", jas.name)
        self.assertEqual("20", jas.port_shift)

        # should begin at 1 again as it is a different group
        jas = ImplementationDescription.class_for_name('jbossas')(host=self.i1_1, group=self.i6_2 , _env=self.e1)
        self.assertEqual("ErpAsDev1_02_01", jas.name)
        self.assertEqual("30", jas.port_shift)

        jas = ImplementationDescription.class_for_name('jbossas')(host=self.i1_2, group=self.i6_2 , _env=self.e1)
        self.assertEqual("ErpAsDev1_02_02", jas.name)
        self.assertEqual("10", jas.port_shift)


