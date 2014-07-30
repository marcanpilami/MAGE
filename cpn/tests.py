# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Django imports
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

## MAGE imports
from ref.creation import duplicate_envt
from ref.models import ComponentInstance, Convention
from ref.models import Application, LogicalComponent, \
    ComponentImplementationClass, EnvironmentType, Environment
from cpn.models import  OracleInstance, OracleSchema, WasCell, \
    GlassfishAS, MqQueueManagerParams, MqQueueManager, WasNode, WasCluster, \
    WasAS, WasApplication, ApplicationBinary, OsServer

class TestHelper:
    def __init__(self):
        self.envt_prd1 = Environment.objects.get(name='PRD1')
        self.envt_tec2 = Environment.objects.get(name='TEC2')
        self.envt_dev1 = Environment.objects.get(name='DEV1')
        
        self.logical_rdbms_module1 = LogicalComponent.objects.get(name='RDBMS container for module 1')
        self.logical_rdbms_module2 = LogicalComponent.objects.get(name='RDBMS container for module 2')
        self.logical_ejb_int = LogicalComponent.objects.get(name='EJB container for integration platform')
        self.logical_ejb_usr = LogicalComponent.objects.get(name='EJB container for user web apps')
        self.logical_mqc_int = LogicalComponent.objects.get(name='Queuing broker cfg for integration platform')
        self.logical_mqc_usr = LogicalComponent.objects.get(name='Queuing broker cfg for user web apps')
    
        self.et_prd = EnvironmentType.objects.get(short_name='PRD')
        self.et_fcf = EnvironmentType.objects.get(short_name='FCF')
        self.et_tcf = EnvironmentType.objects.get(short_name='TCF')
        self.et_int = EnvironmentType.objects.get(short_name='INT')
        self.et_dev = EnvironmentType.objects.get(short_name='DEV')
    
        self.cic_rdbms_module1_oracle_mut = ComponentImplementationClass.objects.get(name="oracle_module1")
        self.cic_rdbms_module1_postgres_dedicated = ComponentImplementationClass.objects.get(name="postgres_module1")
        self.cic_rdbms_module2_oracle_mut = ComponentImplementationClass.objects.get(name="oracle_module2")
        self.cic_ejb_int_was = ComponentImplementationClass.objects.get(name="was_int")
        self.cic_ejb_usr_was = ComponentImplementationClass.objects.get(name="was_usr")
        self.cic_ejb_usr_gla = ComponentImplementationClass.objects.get(name="glassfish_usr")
        self.cic_mqc_int_wmq = ComponentImplementationClass.objects.get(name="mq_int")
        self.cic_mqc_usr_wmq = ComponentImplementationClass.objects.get(name="mq_usr")
        
        self.ci_ora_1 = OracleSchema.objects.get(name='prd_int')
        

def utility_create_test_envt(i):
    a1 = Application(name='application %s' % i)
    a1.save()
    
    l1 = LogicalComponent(name='RDBMS container for module 1', description="description", application=a1, ref1='module1')
    l1.save()
    l2 = LogicalComponent(name='RDBMS container for module 2', description="description", application=a1, ref1='module2')
    l2.save()
    l3 = LogicalComponent(name='EJB container for integration platform', description="description", application=a1, scm_trackable=False)
    l3.save()
    l4 = LogicalComponent(name='EJB container for user web apps', description="description", application=a1, scm_trackable=False)
    l4.save()
    l5 = LogicalComponent(name='Queuing broker cfg for integration platform', description="description", application=a1)
    l5.save()
    l6 = LogicalComponent(name='Queuing broker cfg for user web apps', description="description", application=a1)
    l6.save()
    l7 = LogicalComponent(name='integration application binaries (batch)', description="description", application=a1)
    l7.save()
    
    et1 = EnvironmentType(name='production', description="description", short_name='PRD', chronological_order=5)
    et2 = EnvironmentType(name='functional conformity', description="description", short_name='FCF', chronological_order=4)
    et3 = EnvironmentType(name='technical conformity', description="description", short_name='TCF', chronological_order=2)
    et4 = EnvironmentType(name='integration tests', description="description", short_name='INT', chronological_order=3)
    et5 = EnvironmentType(name='development', description="description", short_name='DEV', chronological_order=1)
    et1.save()
    et2.save()
    et3.save()
    et4.save()
    et5.save()
    
    impl_1_1 = ComponentImplementationClass(name='oracle_module1', description='Oracle schema for module 1 in a mutualized instance', implements=l1, python_model_to_use=ContentType.objects.get_for_model(OracleSchema))
    impl_1_2 = ComponentImplementationClass(name='postgres_module1', description='Dedicated PS database for module 1', implements=l1, python_model_to_use=ContentType.objects.get_for_model(OracleSchema))
    impl_2_1 = ComponentImplementationClass(name='oracle_module2', description='Oracle schema for module 2 in a mutualized instance', implements=l2, python_model_to_use=ContentType.objects.get_for_model(OracleSchema))
    impl_3_1 = ComponentImplementationClass(name='was_int', description='Websphere AS cluster integration platform in mutualized WAS cell', implements=l3, python_model_to_use=ContentType.objects.get_for_model(WasCell))
    impl_4_1 = ComponentImplementationClass(name='was_usr', description='Mutualized WAS cell', implements=l4, python_model_to_use=ContentType.objects.get_for_model(WasCell))
    impl_4_2 = ComponentImplementationClass(name='glassfish_usr', description='Glassfish dedicated AS instance for user app platform', implements=l4, python_model_to_use=ContentType.objects.get_for_model(GlassfishAS))
    impl_5_1 = ComponentImplementationClass(name='mq_int', description='MQ Series integration app configuration in mutualized MQ broker', implements=l5, python_model_to_use=ContentType.objects.get_for_model(MqQueueManagerParams))
    impl_6_1 = ComponentImplementationClass(name='mq_usr', description='MQ Series user web app configuration in mutualized MQ broker', implements=l6, python_model_to_use=ContentType.objects.get_for_model(MqQueueManagerParams))
    impl_7_1 = ComponentImplementationClass(name='batch_int', description='integration application batch Java binaries', implements=l7, python_model_to_use=ContentType.objects.get_for_model(ApplicationBinary))
    impl_1_1.save()
    impl_1_2.save()
    impl_2_1.save()
    impl_3_1.save()
    impl_4_1.save()
    impl_4_2.save()
    impl_5_1.save()
    impl_6_1.save()
    impl_7_1.save()
    
    et1.implementation_patterns.add(impl_1_1, impl_2_1, impl_3_1, impl_4_1, impl_5_1, impl_6_1)  # # PRD
    et3.implementation_patterns.add(impl_1_1, impl_2_1, impl_3_1, impl_4_1, impl_5_1, impl_6_1)  # # TEC
    et5.implementation_patterns.add(impl_1_2, impl_2_1, impl_3_1, impl_4_2, impl_5_1, impl_6_1)  # # DEV has a dedicated db so they can destroy it.
    
    e1 = Environment(name='PRD1', typology=et1, description='production envt')
    e1.save()
    e2 = Environment(name='DEV1', typology=et5, description='development environment for editor teams')
    e2.save()
    e3 = Environment(name='DEV2', typology=et5, description='development environment for integrator teams')
    e3.save()
    e4 = Environment(name='TEC1', typology=et3, description='technical team\'s sandbox')
    e4.save()
    e5 = Environment(name='TEC2', typology=et3, description='for packaging tests')
    e5.save()
    e6 = Environment(name='TEC3', typology=et3, description='staging environment used for request fulfillment - partial restoration, parameter test...')
    e6.save()
    
    us1 = OsServer(name='srv_server_dev', os='AIX', admin_account_login='root', admin_account_password='password')
    us1.save()
    us2 = OsServer(name='srv_tsts_oracle', os='AIX', admin_account_login='root', admin_account_password='password')
    us2.save()
    us3 = OsServer(name='srv_tsts_was', os='AIX', admin_account_login='root', admin_account_password='password')
    us3.save()
    us4 = OsServer(name='srv_prd_oracle', os='AIX', admin_account_login='root', admin_account_password='password')
    us4.save()
    us5 = OsServer(name='srv_prd_was_user', os='AIX', admin_account_login='root', admin_account_password='password')
    us5.save()
    us6 = OsServer(name='srv_prd_was_integration', os='AIX', admin_account_login='root', admin_account_password='password')
    us6.save()
    
    oi1 = OracleInstance(name='ORAINST1')
    oi1.save()
    oi1.server = us1
    oi2 = OracleInstance(name='ORAINST2')
    oi2.save()
    oi2.server = us2
    oi3 = OracleInstance(name='ORAINST3')
    oi3.save()
    oi3.server = us4
    
    mq1 = MqQueueManager(name="MQDEVALL", port=123)
    mq1.save()
    mq1.server = us1
    mq2 = MqQueueManager(name='MQTSTALL', port=123)
    mq2.save()
    mq2.server = us3
    mq3 = MqQueueManager(name='MQPRDINT', port=123)
    mq3.save()
    mq3.server = us6
    mq4 = MqQueueManager(name='MQTSTUSR', port=123)
    mq4.save()
    mq4.server = us5
    
    mqp1 = MqQueueManagerParams(instanciates=impl_5_1)
    mqp1.save()
    mqp1.qm = mq1
    mqp1.environments.add(e2)
    mqp2 = MqQueueManagerParams(instanciates=impl_6_1)
    mqp2.save()
    mqp2.qm = mq1
    mqp2.environments.add(e2)
    
    mqp3 = MqQueueManagerParams(instanciates=impl_5_1)
    mqp3.save()
    mqp3.qm = mq2
    mqp3.environments.add(e5)
    mqp4 = MqQueueManagerParams(instanciates=impl_6_1)
    mqp4.save()
    mqp4.qm = mq2
    mqp4.environments.add(e5)
    
    mqp5 = MqQueueManagerParams(instanciates=impl_5_1)  # PRD, INT
    mqp5.save()
    mqp5.qm = mq3
    mqp5.environments.add(e1)
    mqp6 = MqQueueManagerParams(instanciates=impl_6_1)  # PRD, USR
    mqp6.save()
    mqp6.qm = mq4
    mqp6.environments.add(e1)
    
    
    
    wasCell1 = WasCell(name='wcellDEV')
    wasCell1.save()
    wasCell1.manager_server = us1
    wasCell2 = WasCell(name='wcellTST')
    wasCell2.save()
    wasCell2.manager_server = us3
    wasCell3 = WasCell(name='wcellPRD')
    wasCell3.save()
    wasCell3.manager_server = us5
    
    wasNode1 = WasNode(name='wnDEV')
    wasNode1.save()
    wasNode1.server = us1
    wasNode1.was_cell = wasCell1
    wasNode2 = WasNode(name='wnTST')
    wasNode2.save()
    wasNode2.server = us3
    wasNode2.was_cell = wasCell2
    wasNode3 = WasNode(name='wnPRDINT')
    wasNode3.save()
    wasNode3.server = us5
    wasNode3.was_cell = wasCell3
    wasNode4 = WasNode(name='wnPRDUSR')
    wasNode4.save()
    wasNode4.server = us6
    wasNode4.was_cell = wasCell3
    
    wasCluster1 = WasCluster(name='wcluDEV')
    wasCluster1.save()
    wasCluster1.was_cell = wasCell1
    wasCluster1.environments.add(e2)
    wasCluster2 = WasCluster(name='wcluTST')
    wasCluster2.save()
    wasCluster2.was_cell = wasCell2
    wasCluster2.environments.add(e5)
    wasCluster3 = WasCluster(name='wcluPRDINT')
    wasCluster3.save()
    wasCluster3.was_cell = wasCell3
    wasCluster3.environments.add(e1)
    wasCluster4 = WasCluster(name='wcluPRDUSR')
    wasCluster4.save()
    wasCluster4.was_cell = wasCell3
    wasCluster4.environments.add(e1)
        
    wasAs1 = WasAS(name='waDEV')
    wasAs1.save()
    wasAs1.was_node = wasNode1
    wasAs1.was_cluster = wasCluster1
    wasAs1.environments.add(e2)
    wasAs2 = WasAS(name='waTST')
    wasAs2.save()
    wasAs2.was_node = wasNode2
    wasAs2.was_cluster = wasCluster2
    wasAs2.environments.add(e5)
    wasAs3 = WasAS(name='waPRDINT1')
    wasAs3.save()
    wasAs3.was_node = wasNode3
    wasAs3.was_cluster = wasCluster3
    wasAs3.environments.add(e1)
    wasAs4 = WasAS(name='waPRDUSR1')
    wasAs4.save()
    wasAs4.was_node = wasNode3
    wasAs4.was_cluster = wasCluster4
    wasAs4.environments.add(e1)
    wasAs5 = WasAS(name='waPRDINT2')
    wasAs5.save()
    wasAs5.was_node = wasNode4
    wasAs5.was_cluster = wasCluster3
    wasAs5.environments.add(e1)
    wasAs6 = WasAS(name='waPRDUSR2')
    wasAs6.save()
    wasAs6.was_node = wasNode4
    wasAs6.was_cluster = wasCluster4
    wasAs6.environments.add(e1)
    
    wasApp1 = WasApplication(name='integration')
    wasApp1.save()
    wasApp1.was_cluster = wasCluster3
    wasApp1.environments.add(e1)
    
    wasApp2 = WasApplication(name='user web UI')
    wasApp2.save()
    wasApp2.was_cluster = wasCluster4
    wasApp2.environments.add(e1)
    
    
    #### PRODUCTION
    os1 = OracleSchema(name='prd_int', password='toto', instanciates=impl_1_1)
    os1.save()
    os2 = OracleSchema(name='prd_user', password='toto', instanciates=impl_2_1)
    os2.save()
    os1.environments.add(e1)
    os2.environments.add(e1)
    os1.oracle_instance = oi3
    os2.oracle_instance = oi3

    bin1 = ApplicationBinary(name='batchs', root_directory='/batch/PRD1', instanciates=impl_7_1)
    bin1.save()
    bin1.environments.add(e1)
    bin1.server = us6
    bin1.connectedTo.add(os1)
        
    wasApp1.connectedTo.add(mqp5, os1)  # # PRD, INT
    wasApp2.connectedTo.add(mqp6, os2)  # # PRD, USR
    mqp5.connectedTo.add(mqp6)
    
    
    #### TEC2
    tec2_os1 = OracleSchema(name='tec2_int', password='toto', instanciates=impl_1_1)
    tec2_os1.save()
    tec2_os1.environments.add(e5)
    tec2_os1.oracle_instance = oi1
    
    return a1


class SimpleTest(TestCase):
    def test_creation(self):
        """
        Tests that it is possible to create an instance
        """
        i = OracleInstance(port=123, listener="LISTENER")
        
        self.assertEqual(i.port, 123)
    
    def test_parents_and_polymorphism(self):
        """
        Tests that it is possible to access the auto fields from an instance
        """
        i = OracleInstance(port=123, listener="LISTENER")
        d = OsServer(name='test', os='AIX', admin_account_login='root', admin_account_password='password')
        i.save()
        d.save()
        
        i.server = d
        i.save()
        
        self.assertEqual(i.port, 123)
        self.assertNotEqual(i.server, None)
        self.assertEqual(i.server.name, 'test')      
        
        r = ComponentInstance.objects.get(pk=i.pk)
        self.assertNotEqual(r.leaf, None)
        self.assertEqual(r.leaf.server.name, 'test') 

    def test_description(self):
        i = OracleInstance(name='SUPERINSTANCE', port=123, listener="LISTENER")
        i.save()
        self.assertEqual(i.__unicode__(), 'SUPERINSTANCE (None)')
        
    def test_fullapp(self):
        utility_create_test_envt(1)
        
    def test_duplication_nc(self):
        utility_create_test_envt(1)
        
        helper = TestHelper()
        
        e1 = helper.envt_prd1
        e1.typology.default_convention = Convention.objects.all()[0]
        wa1 = e1.component_instances.get(instanciates__implements__ref1="module1")
        old_name = wa1.name
        
        e2 = duplicate_envt(e1.name, "RACCOON1", {})
        wa1 = e1.component_instances.get(instanciates__implements__ref1="module1")
        wa2 = e2.component_instances.get(instanciates__implements__ref1="module1")
        
        self.assert_("module1_raccoon1", wa2.name)
        self.assert_(old_name, wa1.name)
            

