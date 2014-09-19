# coding: utf-8
from django.test import TestCase
from ref.naming_language import resolve
from ref.demo_items import utility_create_meta, utility_create_logical
from ref.models import ImplementationDescription, Environment
from ref import mql
from ref.models.models import EnvironmentType, ComponentInstance

class MCLTestCase(TestCase):
    def setUp(self):
        utility_create_meta()
        utility_create_logical()

        e1 = Environment(name='DEV1', description='DEV1', typology=EnvironmentType.objects.get(short_name='DEV'))
        e1.save()

        i1_1 = ImplementationDescription.class_for_name('osserver')(dns='server1.marsu.net', admin_login='test admin')
        i1_2 = ImplementationDescription.class_for_name('osserver')(dns='server2.marsu.net', admin_login='test admin')

        i12_1 = ImplementationDescription.class_for_name('jbossdomain')(name=u'domain1', admin_user='admin', admin_password='pass', \
                base_http_port=8080, base_https_port=8081, web_admin_port=9990, native_admin_port=9999)

        i13_1 = ImplementationDescription.class_for_name('jbosshost')(name=u'jbosshost1.marsu.net', domain=i12_1, server=i1_1)
        i13_2 = ImplementationDescription.class_for_name('jbosshost')(name=u'jbosshost2.marsu.net', domain=i12_1, server=i1_2)

        self.i14_1 = ImplementationDescription.class_for_name('jbossgroup')(name=u'GEP_DEV1_01', dns_to_use='marsu.pl', \
                   dedicated_admin_login='dev1', dedicated_admin_password='dev1', domain=i12_1)
        self.i14_2 = ImplementationDescription.class_for_name('jbossgroup')(name=u'GEP_DEV1_02', dns_to_use='marsu2.pl', \
                   dedicated_admin_login='dev1', dedicated_admin_password='dev1', domain=i12_1)

        self.i15_1_1 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_01_01', port_shift=00, host=i13_1, group=self.i14_1)
        self.i15_1_2 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_01_02', port_shift=00, host=i13_1, group=self.i14_1)
        self.i15_1_3 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_01_03', port_shift=00, host=i13_2, group=self.i14_1, _env=e1)
        self.i15_2_1 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_02_01', port_shift=00, host=i13_1, group=self.i14_2)

        self.i16_1 = ImplementationDescription.class_for_name('jbossapplication')(name=u'GEP_DEV1_APP1', context_root='/app1', group=self.i14_1, _cic='soft1_webapp_ee6_jboss')
        self.i16_1.save()

    def test_all_query(self):
        res = mql.run("SELECT instances")
        self.assertEqual(len(res), ComponentInstance.objects.all().count())

    def test_pre_query(self):
        res = mql.run("SELECT offer 'soft1_webapp_ee6_jboss' INSTANCES")
        self.assertEqual(1, len(res))
        
        res2 = mql.run("SELECT lc 'web application EE6' INSTANCES")
        self.assertEqual(1, len(res2))
        
        self.assertEqual(res[0]['_id'], res2[0]['_id'])
        
        res3 = mql.run("SELECT lc 'web application EE6'  offer 'soft1_webapp_ee6_jboss' 'jbossapplication' INSTANCES")
        self.assertEqual(1, len(res3))
        

    def test_query_where_one_level_one_predicate(self):
        res = mql.run("SELECT INSTANCES where name='GEP_DEV1_01_03'")
        self.assertEqual(1, len(res))

    def test_query_where_one_level_two_predicates(self):
        res = mql.run("SELECT INSTANCES where name='GEP_DEV1_01_03' and port_shift='0'")
        self.assertEqual(1, len(res))

    def test_query_where_two_levels_one_predicate(self):
        res = mql.run("SELECT 'jbossas' INSTANCES where group.name='GEP_DEV1_01'")
        #print res
        #print [p.id for p in res]
        self.assertEqual(3, len(res))

    def test_query_where_three_levels_two_predicates(self):
        res = mql.run("SELECT 'jbossas' INSTANCES where group.domain.name='domain1' and name='GEP_DEV1_01_03'")
        self.assertEqual(1, len(res))

    def test_query_where_id(self):
        res = mql.run("SELECT INSTANCES where _id='%s'" % self.i15_1_1._instance.id)
        self.assertEqual(1, len(res))
        self.assertEqual(self.i15_1_1._instance.id, res[0]['_id'])

    def test_query_where_sub_id(self):
        res = mql.run("SELECT INSTANCES where group._id='%s'" % self.i14_2._instance.id)
        self.assertEqual(1, len(res))
        self.assertEqual(self.i15_2_1._instance.id, res[0]['_id'])

    def test_query_where_envt(self):
        res = mql.run("SELECT environment 'DEV1' 'jbossas' INSTANCES")
        self.assertEqual(1, len(res))
        self.assertEqual(self.i15_1_3._instance.id, res[0]['_id'])

    
    def test_query_selector_simple(self):
        res = mql.run("SELECT name,group.name,group.domain.name FROM 'jbossas' INSTANCES WHERE name='GEP_DEV1_01_03'")
        self.assertEqual(1, len(res))
        self.assertEqual(res[0]['name'], 'GEP_DEV1_01_03')
        
    def Xtest_query_db_impact(self):
        self.assertNumQueries(0, lambda : mql.run("SELECT INSTANCES where name='GEP_DEV1_01_03'"))
        self.assertNumQueries(1, lambda : mql.run("SELECT INSTANCES where name='GEP_DEV1_01_03'").count())
        
        #self.assertNumQueries(2, lambda : mql.run("SELECT name FROM INSTANCES where name='GEP_DEV1_01_03'"))
        
        self.assertNumQueries(3, lambda : mql.run("SELECT name,group.name FROM INSTANCES where name='GEP_DEV1_01_03'"))

    def test_query_where_subquery(self):
        res = mql.run("SELECT 'jbossas' INSTANCES where group.name=(SELECT name FROM INSTANCES WHERE name='GEP_DEV1_02')")
        self.assertEqual(1, len(res))
        self.assertEqual(self.i15_2_1._instance.id, res[0]['_id'])
