# coding: utf-8
from django.test import TestCase
from ref.naming_language import resolve
from ref.demo_items import utility_create_meta
from ref.models.models import ImplementationDescription, Project, Application, \
    EnvironmentType, Environment, LogicalComponent, ComponentImplementationClass

class NLTestCase(TestCase):
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

        e1 = Environment(name='DEV1', description='DEV1', typology=et1)
        e1.save()
        p1.environment_set.add(e1)

        l3 = LogicalComponent(name='web application EE6', description="The new EE6 application", application=a1, ref1='pu6')
        l3.save()
        impl_3_2 = ComponentImplementationClass(name='soft1_webapp_ee6_jboss', description='SOFT1 EE6 web app in a JBoss ear/war package', implements=l3, \
                                                technical_description=ImplementationDescription.objects.get(name='jbossapplication'))
        impl_3_2.save()

        i1_1 = ImplementationDescription.class_for_name('osserver')(dns='server1.marsu.net', admin_login='test admin')

        i12_1 = ImplementationDescription.class_for_name('jbossdomain')(name=u'domain1', admin_user='admin', admin_password='pass', \
                base_http_port=8080, base_https_port=8081, web_admin_port=9990, native_admin_port=9999, _env=e1)

        i13_1 = ImplementationDescription.class_for_name('jbosshost')(name=u'jbosshost1.marsu.net', domain=i12_1, server=i1_1)

        i14_1 = ImplementationDescription.class_for_name('jbossgroup')(name=u'GEP_DEV1_01', dns_to_use='marsu.pl', \
                   dedicated_admin_login='dev1', dedicated_admin_password='dev1', domain=i12_1, _env=e1)
        i14_1.profile = ""

        self.i15_1_1 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_01_01', port_shift=00, host=i13_1, group=i14_1, _env=e1)

        self.i16_1 = ImplementationDescription.class_for_name('jbossapplication')(name=u'GEP_DEV1_APP1', context_root='/app1', group=i14_1, _cic='soft1_webapp_ee6_jboss', _env=e1)
        self.i16_1.save()


    def test_navigation_simple(self):
        res = resolve('name', self.i16_1)
        self.assertEqual("GEP_DEV1_APP1", res)

    def test_navigation_dotted(self):
        res = resolve('group.domain.name', self.i16_1)
        self.assertEqual("domain1", res)

    def test_string(self):
        res = resolve('"houbahop"', self.i16_1)
        self.assertEqual("houbahop", res)

    def test_operation_simple_plus(self):
        res = resolve('50+10', self.i16_1)
        self.assertEqual(60, res)

    def test_operation_simple_minus(self):
        res = resolve('50-10', self.i16_1)
        self.assertEqual(40, res)

    def test_operation_simple_mult(self):
        res = resolve('50*10', self.i16_1)
        self.assertEqual(500, res)

    def test_operation_simple_div(self):
        res = resolve('50/10', self.i16_1)
        self.assertEqual(5, res)

    def test_operation_with_navigation(self):
        res = resolve('group.domain.base_http_port+100', self.i16_1)
        self.assertEqual(8180, res)

    def test_alternative_first(self):
        res = resolve("1?2?3", self.i16_1)
        self.assertEqual(1, res)

    def test_alternative_second(self):
        res = resolve("group.profile?2?3", self.i16_1)
        self.assertEqual(2, res)

    def test_alternative_third(self):
        res = resolve("group.profile?group.profile?3", self.i16_1)
        self.assertEqual(3, res)

    def test_concat_two(self):
        res = resolve('1|2', None)
        self.assertEqual('12', res)

    def test_concat_three(self):
        res = resolve('1|2|3', None)
        self.assertEqual('123', res)

    def test_concat_three_expr(self):
        res = resolve('1|2|(3|4)', None)
        self.assertEqual('1234', res)

    def test_concat_navigation(self):
        res = resolve('1|group.name', self.i16_1)
        self.assertEqual('1GEP_DEV1_01', res)

        res = resolve('1|group.name|3', self.i16_1)
        self.assertEqual('1GEP_DEV1_013', res)

        res = resolve('group.name|2', self.i16_1)
        self.assertEqual('GEP_DEV1_012', res)

    def test_alternative_concat_protection(self):
        res = resolve('1|2?3', None)
        self.assertEqual("12", res)

    def test_parsing_real_1(self):
        pattern = 'client_url?("http://"|(group.dns_to_use?group.domain.name)|":"|(group.domain.base_http_port+10))'
        res = resolve(pattern, self.i16_1)
        self.assertEqual("http://marsu.pl:8090", res)
