# coding: utf-8
from django.test import TestCase
from ref.demo_items import utility_create_meta, utility_create_logical
from ref.models import ImplementationDescription, Environment, EnvironmentType, ComponentInstance, Project
from ref import mql
from django.db.models import Q


class MQLTestCase(TestCase):
    def setUp(self):
        utility_create_meta()
        utility_create_logical()

        e1 = Environment(name='DEV1', description='DEV1', typology=EnvironmentType.objects.get(short_name='DEV'), project=Project.objects.get(name='SUPER-PROJECT'))
        e1.save()
        p1 = e1.project

        i1_1 = ImplementationDescription.class_for_name('osserver')(_project=p1, dns='server1.marsu.net', admin_login='test admin', _noconventions=True)
        i1_2 = ImplementationDescription.class_for_name('osserver')(_project=p1, dns='server2.marsu.net', admin_login='test admin', _noconventions=True)

        i12_1 = ImplementationDescription.class_for_name('jbossdomain')(_project=p1, name=u'domain1', admin_user='admin', admin_password='pass', \
                base_http_port=8080, base_https_port=8081, web_admin_port=9990, native_admin_port=9999, _noconventions=True)

        i13_1 = ImplementationDescription.class_for_name('jbosshost')(_project=p1, name=u'jbosshost1.marsu.net', domain=i12_1, server=i1_1, _noconventions=True)
        i13_2 = ImplementationDescription.class_for_name('jbosshost')(_project=p1, name=u'jbosshost2.marsu.net', domain=i12_1, server=i1_2, _noconventions=True)

        self.i14_1 = ImplementationDescription.class_for_name('jbossgroup')(_project=p1, name=u'GEP_DEV1_01', dns_to_use='marsu.pl', \
                   dedicated_admin_login='dev1', dedicated_admin_password='dev1', domain=i12_1, _noconventions=True)
        self.i14_2 = ImplementationDescription.class_for_name('jbossgroup')(_project=p1, name=u'GEP_DEV1_02', dns_to_use='marsu2.pl', \
                   dedicated_admin_login='dev1', dedicated_admin_password='dev1', domain=i12_1, _noconventions=True)

        self.i15_1_1 = ImplementationDescription.class_for_name('jbossas')(_project=p1, name=u'GEP_DEV1_01_01', port_shift=00, host=i13_1, group=self.i14_1, _noconventions=True)
        self.i15_1_2 = ImplementationDescription.class_for_name('jbossas')(_project=p1, name=u'GEP_DEV1_01_02', port_shift=00, host=i13_1, group=self.i14_1, _noconventions=True)
        self.i15_1_3 = ImplementationDescription.class_for_name('jbossas')(_project=p1, name=u'GEP_DEV1_01_03', port_shift=00, host=i13_2, group=self.i14_1, _env=e1, _noconventions=True)
        self.i15_2_1 = ImplementationDescription.class_for_name('jbossas')(_project=p1, name=u'GEP_DEV1_02_01', port_shift=00, host=i13_1, group=self.i14_2, _noconventions=True)

        self.i16_1 = ImplementationDescription.class_for_name('jbossapplication')(_project=p1, name=u'GEP_DEV1_APP1', context_root='/app1', group=self.i14_1, _cic='soft1_webapp_ee6_jboss', _noconventions=True)
        self.i16_1.save()

    def test_all_query(self):
        res = mql.run("SELECT instances", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(len(res), ComponentInstance.objects.filter(Q(environments__project__name='SUPER-PROJECT') | Q(environments__project__isnull=True)).count())

    def test_pre_query(self):
        res = mql.run("SELECT offer 'soft1_webapp_ee6_jboss' INSTANCES", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res))

        res2 = mql.run("SELECT lc 'web application EE6' INSTANCES", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res2))

        self.assertEqual(res[0]['mage_id'], res2[0]['mage_id'])

        res3 = mql.run("SELECT lc 'web application EE6'  offer 'soft1_webapp_ee6_jboss' 'jbossapplication' INSTANCES", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res3))


    def test_query_where_one_level_one_predicate(self):
        res = mql.run("SELECT INSTANCES where name='GEP_DEV1_01_03'", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res))

    def test_query_where_one_level_two_predicates(self):
        res = mql.run("SELECT INSTANCES where name='GEP_DEV1_01_03' and port_shift='0'", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res))

    def test_query_where_two_levels_one_predicate(self):
        res = mql.run("SELECT 'jbossas' INSTANCES where group.name='GEP_DEV1_01'", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(3, len(res))

    def test_query_where_three_levels_two_predicates(self):
        res = mql.run("SELECT 'jbossas' INSTANCES where group.domain.name='domain1' and name='GEP_DEV1_01_03'", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res))

    def test_query_where_id(self):
        res = mql.run("SELECT INSTANCES where _id='%s'" % self.i15_1_1._instance.id, Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res))
        self.assertEqual(self.i15_1_1._instance.id, res[0]['mage_id'])

    def test_query_where_sub_id(self):
        res = mql.run("SELECT INSTANCES where group._id='%s'" % self.i14_2._instance.id, Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res))
        self.assertEqual(self.i15_2_1._instance.id, res[0]['mage_id'])

    def test_query_where_envt(self):
        res = mql.run("SELECT environment 'DEV1' 'jbossas' INSTANCES", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res))
        self.assertEqual(self.i15_1_3._instance.id, res[0]['mage_id'])


    def test_query_selector_simple(self):
        res = mql.run("SELECT name,group.name,group.domain.name FROM 'jbossas' INSTANCES WHERE name='GEP_DEV1_01_03'", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res))
        self.assertEqual(res[0]['name'], 'GEP_DEV1_01_03')

    def Xtest_query_db_impact(self):
        self.assertNumQueries(0, lambda : mql.run("SELECT INSTANCES where name='GEP_DEV1_01_03'", Project.objects.get(name='SUPER-PROJECT')))
        self.assertNumQueries(1, lambda : mql.run("SELECT INSTANCES where name='GEP_DEV1_01_03'", Project.objects.get(name='SUPER-PROJECT')).count())

        #self.assertNumQueries(2, lambda : mql.run("SELECT name FROM INSTANCES where name='GEP_DEV1_01_03'", Project.objects.get(name='SUPER-PROJECT')))

        self.assertNumQueries(3, lambda : mql.run("SELECT name,group.name FROM INSTANCES where name='GEP_DEV1_01_03'", Project.objects.get(name='SUPER-PROJECT')))

    def test_query_where_subquery(self):
        res = mql.run("SELECT 'jbossas' INSTANCES where group.name=(SELECT name FROM INSTANCES WHERE name='GEP_DEV1_02')", Project.objects.get(name='SUPER-PROJECT'))
        self.assertEqual(1, len(res))
        self.assertEqual(self.i15_2_1._instance.id, res[0]['mage_id'])
