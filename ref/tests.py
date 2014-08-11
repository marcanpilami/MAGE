# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Django imports
from django.test import TestCase

## MAGE imports
from ref.models import  EnvironmentType, ImplementationRelationType, ImplementationDescription, Project, Application, LogicalComponent, ComponentImplementationClass, \
    Environment


def utility_create_meta():
    ## Relations classification
    dt1 = ImplementationRelationType(name='connectedTo')
    dt2 = ImplementationRelationType(name='dependsOn')
    dt1.save()
    dt2.save()

    ######################################################################
    ## Server
    ######################################################################

    ## OS Server
    impl1 = ImplementationDescription.create_or_update('osserver', 'a server with an installed OS', self_description_pattern='server |%dns', tag='os').\
            add_field_simple('dns', 'dns to use for admin login').\
            add_field_simple('admin_login', 'login to use for admin access', default='root').\
            add_field_simple('admin_password', 'password to use for admin access', sensitive=True)
    impl1.save()

    ## OS account
    impl2 = ImplementationDescription.create_or_update('osaccount', 'account for login on a server', self_description_pattern='%login', tag='os').\
            add_field_simple('login', 'the acocunt login').\
            add_field_simple('password', 'password corresponding to the login', sensitive=True).\
            add_relationship('server', 'server corresponding to the login', impl1, dt2, 1, 1)
    impl2.save()


    ######################################################################
    ## Oracle
    ######################################################################

    ## Oracle instance
    impl3 = ImplementationDescription.create_or_update('oracleinstance', 'an oracle instance', self_description_pattern='instance |%sid', tag='oracle').\
            add_field_simple('sid', 'instance SID').\
            add_field_simple('admin_login', 'login to use for DBA access').\
            add_field_simple('admin_password', 'password to use for DBA access').\
            add_field_simple('port', 'instance port', default=1521).\
            add_field_computed('server_name', 'name of the server', 'toto|%server.name').\
            add_field_computed('test_p', 'test overload', 'toto|%server.admin_password;server.admin_login').\
            add_relationship('server', 'server on which the instance is running', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl3.save()

    ## Oracle schema
    impl4 = ImplementationDescription.create_or_update('oracleschema', 'schema on an Oracle instance', self_description_pattern='%name| on |%instance.sid', tag='oracle').\
            add_field_simple('name', 'name').\
            add_field_simple('password', 'password', sensitive=True).\
            add_field_simple('dns_to_use', 'overload of the server DNS (service address)').\
            add_field_simple('service_name_to_use', 'service name (if empty, SID will be used)').\
            add_field_computed('conn_str', 'sqlplus connection string', '%name|/|%password|@|%service_name_to_use;instance.sid', sensitive=True).\
            add_field_computed('jdbc', 'JDBC connection string', 'jdbc:oracle:thin:@//|%dns_to_use;instance.server.dns|:|%instance.port|/|%service_name_to_use;instance.sid').\
            add_relationship('instance', 'instance holding the schema', impl3, dt2, min_cardinality=1, max_cardinality=1)
    impl4.save()

    ## Oracle package
    impl5 = ImplementationDescription.create_or_update('oraclepackage', 'package inside an Oracle schema', self_description_pattern='%name', tag='oracle').\
            add_field_simple('name', 'instance SID').\
            add_relationship('schema', 'schema holding the package', impl4, dt2, min_cardinality=1, max_cardinality=1)
    impl5.save()


    ######################################################################
    ## Message Oriented Middlewares
    ######################################################################

    ## MQ series broker
    impl6 = ImplementationDescription.create_or_update('mqseriesmanager', 'Websphere MQ broker', self_description_pattern='%name', tag='mq').\
            add_field_simple('name', 'broker name').\
            add_field_simple('port', 'listener port', default=1414).\
            add_field_simple('admin_channel', 'name of the admin connection channel', default='SYSTEM.ADMIN.SVRCONN').\
            add_relationship('server', 'instance holding the schema', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl6.save()

    ## MQ series queues configuration
    impl7 = ImplementationDescription.create_or_update('mqseriesparams', 'Websphere MQ broker parameters', self_description_pattern='%name', tag='mq').\
            add_field_simple('name', 'parameter set name').\
            add_relationship('broker', 'target broker', impl6, dt2, min_cardinality=1, max_cardinality=1)
    impl7.save()


    #####################################################################
    ## Batch & JQM
    ######################################################################

    impl8 = ImplementationDescription.create_or_update('applicationfile', 'an application file', self_description_pattern='%name').\
            add_field_simple('name', 'file name').\
            add_field_simple('path', 'path to the file').\
            add_relationship('belongs_to', 'OS user owning the file', impl2, dt2, min_cardinality=0, max_cardinality=1).\
            add_relationship('server', 'server on which the file is stored', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl8.save()


    impl9 = ImplementationDescription.create_or_update('jqmcluster', 'a set of JQM nodes', self_description_pattern='%name', tag='jqm').\
            add_field_simple('name', 'cluster name').\
            add_relationship('schema', 'Oracle schema of the cluster', impl4, dt2, min_cardinality=0, max_cardinality=1)
    impl9.save()

    impl10 = ImplementationDescription.create_or_update('jqmengine', 'moteur JQM', self_description_pattern='%name', tag='jqm').\
            add_field_simple('name', 'JQM node name').\
            add_field_simple('port', 'port HTTP').\
            add_field_simple('jmx_registry_port', 'port registry JMX').\
            add_field_simple('jmx_server_port', 'port serveur JMX').\
            add_field_simple('dl_repo', u'répertoire de stockage des fichiers produits').\
            add_field_simple('job_repo', u'répertoire de stockage des jars utilisateur').\
            add_relationship('cluster', 'member of cluster', impl9, dt2, min_cardinality=1, max_cardinality=1).\
            add_relationship('server', 'server on which the node runs', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl10.save()

    impl11 = ImplementationDescription.create_or_update('jqmbatch', 'batch JQM', self_description_pattern='%name', tag='jqm').\
            add_field_simple('name', 'JQM batch name').\
            add_relationship('cluster', 'runs on cluster', impl9, dt2, min_cardinality=1, max_cardinality=1)
    impl11.save()


    #####################################################################
    ## JBoss 7+ (domain mode)
    ######################################################################

    impl12 = ImplementationDescription.create_or_update('jbossdomain', 'domaine JBoss', self_description_pattern='%name', tag='jboss').\
            add_field_simple('name', 'application name').\
            add_field_simple('admin_user', 'context root', default='/').\
            add_field_simple('admin_password', 'access URL').\
            add_field_simple('base_http_port', 'HTTP port before shifting').\
            add_field_simple('base_https_port', 'HTTPS port before shifting').\
            add_field_simple('web_admin_port', 'admin WS port').\
            add_field_simple('native_admin_port', 'admin native port')
    impl12.save()

    impl13 = ImplementationDescription.create_or_update('jbosshost', u'processus hôte JBoss', self_description_pattern='%name', tag='jboss').\
            add_field_simple('name', 'application name').\
            add_field_computed('admin_port', 'admin port', '%domain.native_admin_port').\
            add_relationship('domain', 'member of domain', impl12, dt2, min_cardinality=1, max_cardinality=1).\
            add_relationship('server', 'run on server', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl13.save()

    impl14 = ImplementationDescription.create_or_update('jbossgroup', u'groupe d\'AS JBoss', self_description_pattern='%name', tag='jboss').\
            add_field_simple('name', 'group name').\
            add_field_simple('profile', 'profil').\
            add_field_simple('dedicated_admin_login', u'utilisateur admin spécifique groupe').\
            add_field_simple('dedicated_admin_password', u'mot de passe spécifique groupe').\
            add_field_simple('dns_to_use', u'service DNS alias').\
            add_field_simple('max_heap_mb', 'Max Heap (Mo)', 384).\
            add_field_simple('max_permgen_mb', 'Max permgen (Mo)', 128).\
            add_field_simple('start_heap_mb', 'Start heap (Mo)', 256).\
            add_field_computed('admin_login', 'admin login', '%dedicated_admin_login;domain.admin_user').\
            add_field_computed('admin_password', 'admin password', '%dedicated_admin_password;domain.admin_password').\
            add_relationship('domain', 'member of domain', impl12, dt2, min_cardinality=1, max_cardinality=1)
    impl14.save()

    impl15 = ImplementationDescription.create_or_update('jbossas', u'JVM JBoss', self_description_pattern='%name', tag='jboss').\
            add_field_simple('name', 'JVM name').\
            add_field_simple('port_shift', 'port shift').\
            add_field_simple('dns_to_use', 'service DNS entry').\
            add_field_computed('http_port', 'actual HTTP port', '%host.domain.base_http_port|+|%port_shift').\
            add_relationship('host', 'runs on host', impl13, dt2, min_cardinality=1, max_cardinality=1).\
            add_relationship('group', 'member of group', impl14, dt2, min_cardinality=1, max_cardinality=1)
            #TODO: basics operations inside computed fields.
    impl15.save()

    impl16 = ImplementationDescription.create_or_update('jbossapplication', 'application JBoss', self_description_pattern='%name', tag='jboss').\
            add_field_simple('name', 'application name').\
            add_field_simple('context_root', 'context root', default='/').\
            add_field_simple('client_url', 'access URL').\
            add_relationship('group', 'member of cluster', impl14, dt2, min_cardinality=1, max_cardinality=1).\
            add_relationship('schema', 'uses Oracle schema', impl4, dt1, min_cardinality=0, max_cardinality=1).\
            add_relationship('broker', 'uses MQ broker', impl6, dt1, min_cardinality=0, max_cardinality=1)
            # add_field_computed('url', 'end-user URL', 'http://|  toto|%server.admin_password;server.admin_login').\
            #TODO: make language recursive...
    impl16.save()


    #####################################################################
    ## WAS 8+ (network deployment mode)
    ######################################################################

    impl17 = ImplementationDescription.create_or_update('wascell', 'WebSphere Application Server Cell', self_description_pattern='%name', tag='was').\
            add_field_simple('name', 'cell name').\
            add_field_simple('manager_port', 'port of network deployment management console', default=9060).\
            add_field_simple('manager_login', 'console admin login', 'admin').\
            add_field_simple('manager_password', 'console admin password', 'password').\
            add_field_computed('url', 'manager URL', 'http://|%manager_server.dns|:|%manager_port|/ibm/console').\
            add_relationship('manager_server', 'server holding the deployment manager node', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl17.save()

    impl18 = ImplementationDescription.create_or_update('wascluster', 'WebSphere Application Server Cluster', self_description_pattern='%name', tag='was').\
            add_field_simple('name', 'application name').\
            add_field_simple('dedicated_admin_user', 'specific account for managing this cluster').\
            add_field_simple('dedicated_admmin__password', 'specific password').\
            add_field_computed('admin_login', 'admin login to use', '%dedicated_admin_user;cell.manager_login').\
            add_field_computed('admin_password', 'admin password to use', '%dedicated_admin_password;cell.manager_password').\
            add_relationship('cell', 'member of cell', impl17, dt2, min_cardinality=1, max_cardinality=1)
    impl18.save()

    impl19 = ImplementationDescription.create_or_update('wasnode', 'WebSphere Application Server Node', self_description_pattern='%name', tag='was').\
            add_field_simple('name', 'node name').\
            add_relationship('server', 'running on server', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl19.save()

    impl20 = ImplementationDescription.create_or_update('wasas', 'WebSphere Application Server JVM', self_description_pattern='%name', tag='was').\
            add_field_simple('name', 'application name').\
            add_field_simple('http_port', 'HTTP port', 9080).\
            add_field_simple('https_port', 'HTTPS port', 8081).\
            add_field_simple('dns_to_use', 'specific service DNS').\
            add_relationship('node', 'member of cell', impl19, dt2, min_cardinality=1, max_cardinality=1).\
            add_relationship('cluster', 'member of cell', impl18, dt2, min_cardinality=1, max_cardinality=1)
    impl20.save()

    impl21 = ImplementationDescription.create_or_update('wasapplication', 'WebSphere Application Server Application', self_description_pattern='%name', tag='was').\
            add_field_simple('name', 'application name').\
            add_field_simple('context_root', 'HTTP port', '/').\
            add_field_simple('client_url', 'service URL').\
            add_field_computed('url', 'access URL', '%client_url').\
            add_relationship('cluster', 'member of cell', impl18, dt2, min_cardinality=1, max_cardinality=1)
    impl21.save()


def utility_create_test_instances():
    ## Environments
    e1 = Environment(name='DEV1', description='DEV1', typology=EnvironmentType.objects.get(short_name='DEV'))
    e1.save()

    ## OS instances
    i1_1 = ImplementationDescription.class_for_name('osserver')(dns='server1.marsu.net', admin_login='test admin')
    i1_2 = ImplementationDescription.class_for_name('osserver')(dns='server2.marsu.net', admin_login='test admin')

    i2_1 = ImplementationDescription.class_for_name('osaccount')(login='user', password='test', server=i1_1)
    i2_1.save()

    ## Oracle items
    i3_1 = ImplementationDescription.class_for_name('oracleinstance')(sid='ORAINST1', server=i1_1, admin_login='login', admin_password='toto')

    i4_1 = ImplementationDescription.class_for_name('oracleschema')(name='schema1', password='pass', instance=i3_1, _env=e1, _cic='soft1_database_main_oracle')
    i4_2 = ImplementationDescription.class_for_name('oracleschema')(name='schema2', password='pass', instance=i3_1, _env=e1, _cic='int_database_main_oracle')
    i4_3 = ImplementationDescription.class_for_name('oracleschema')(name='schema3', password='pass', instance=i3_1)
    i4_1.save()
    i4_2.save()
    i4_3.save()

    ## MQ Series items
    i6_1 = ImplementationDescription.class_for_name('mqseriesmanager')(name='QM.DEV1')

    ## JBoss environment
    i12_1 = ImplementationDescription.class_for_name('jbossdomain')(name=u'domain études', admin_user='admin', admin_password='pass', \
                base_http_port=8080, base_https_port=8081, web_admin_port=9990, native_admin_port=9999)

    i13_1 = ImplementationDescription.class_for_name('jbosshost')(name=u'jbosshost1.marsu.net', domain=i12_1, server=i1_1)
    i13_2 = ImplementationDescription.class_for_name('jbosshost')(name=u'jbosshost2.marsu.net', domain=i12_1, server=i1_2)

    i14_1 = ImplementationDescription.class_for_name('jbossgroup')(name=u'GEP_DEV1_01', profile='DEV1', \
               dedicated_admin_login='dev1', dedicated_admin_password='dev1', domain=i12_1, _env=e1)
    i14_2 = ImplementationDescription.class_for_name('jbossgroup')(name=u'GEP_DEV1_02', profile='DEV1', \
               dedicated_admin_login='dev1', dedicated_admin_password='dev1', domain=i12_1, _env=e1)

    i15_1_1 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_01_01', port_shift=00, host=i13_1, group=i14_1, _env=e1)
    i15_1_2 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_01_02', port_shift=10, host=i13_1, group=i14_1, _env=e1)
    i15_1_3 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_01_03', port_shift=20, host=i13_1, group=i14_1, _env=e1)
    i15_1_4 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_01_04', port_shift=30, host=i13_2, group=i14_1, _env=e1)
    i15_1_5 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_01_05', port_shift=40, host=i13_2, group=i14_1, _env=e1)

    i15_2_1 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_02_01', port_shift=50, host=i13_1, group=i14_2, _env=e1)
    i15_2_2 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_02_02', port_shift=60, host=i13_1, group=i14_2, _env=e1)
    i15_2_3 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_02_03', port_shift=70, host=i13_1, group=i14_2, _env=e1)
    i15_2_4 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_02_04', port_shift=80, host=i13_2, group=i14_2, _env=e1)
    i15_2_5 = ImplementationDescription.class_for_name('jbossas')(name=u'GEP_DEV1_02_05', port_shift=90, host=i13_2, group=i14_2, _env=e1)

    i16_1 = ImplementationDescription.class_for_name('jbossapplication')(name=u'GEP_DEV1_APP1', context_root='/app1', group=i14_1, _cic='soft1_webapp_ee6_jboss', schema=i4_1, _env=e1)
    i16_1.save()
    i16_2 = ImplementationDescription.class_for_name('jbossapplication')(name=u'GEP_DEV1_APP2', context_root='/app2', group=i14_2, _cic='soft1_webapp_legacy_jboss', schema=i4_2, _env=e1)
    i16_2.save()
    i16_2 = ImplementationDescription.class_for_name('jbossapplication')(name=u'GEP_DEV1_APP3', context_root='/app3', group=i14_1, schema=i4_1, _env=e1)
    i16_2.save()

    ## JQM items
    i9_1 = ImplementationDescription.class_for_name('jqmcluster')(name='JqmDev1Cluster', schema=i4_3, _env=e1)
    i10_1 = ImplementationDescription.class_for_name('jqmengine')(name='JqmDev1As_01', port=1789, jmx_registry_port=1889, jmx_server_port=1989, cluster=i9_1, server=i1_1, _env=e1)
    i11_1 = ImplementationDescription.class_for_name('jqmbatch')(name='JqmDev1INT', cluster=i9_1, _cic='int_batch_jqm', _env=e1)
    i11_1.save()


def utility_create_logical():
    p1 = Project(name='SUPER-PROJECT', default_convention=None, description='New ERP for FIRM1. A Big Program project.', alternate_name_1='SUPERCODE', alternate_name_2='ERP')
    p1.save()
    a1 = Application(name='Soft1', description='Super New ERP')
    a1.save()
    a2 = Application(name='Interfaces', description='developments to interface Soft1 with the rest of the FIRM1 systems')
    a2.save()
    p1.applications.add(a1, a2)

    l1 = LogicalComponent(name='main database', description="relational database containing the core Soft1 data", application=a1, ref1='pua')
    l1.save()
    l2 = LogicalComponent(name='web application STRUTS', description="The old Java STRUTS application", application=a1, ref1='pua')
    l2.save()
    l3 = LogicalComponent(name='web application EE6', description="The new EE6 application", application=a1, ref1='pu6')
    l3.save()
    l4 = LogicalComponent(name='web application container', description="Container for EE6 applications", application=a1, scm_trackable=False)
    l4.save()
    # l5 = LogicalComponent(name='Interfaces queue broker config', description="description", application=a2)
    # l5.save()
    l6 = LogicalComponent(name='Interfaces EE6 application', description="description", application=a2)
    l6.save()
    l7 = LogicalComponent(name='main database', description="relational database for the staging needs of the interfaces", application=a2, ref1='int')
    l7.save()
    l8 = LogicalComponent(name='batch jobs', description="batch jobs from the interfaces", application=a2, ref1='int')
    l8.save()

    et1 = EnvironmentType(name='development', description="for developers. No admin except for middlewares.", short_name='DEV', chronological_order=1, default_show_sensitive_data=True)
    et2 = EnvironmentType(name='test', description="for developers. So that they can test their production.", short_name='TST', chronological_order=2, default_show_sensitive_data=True)
    et3 = EnvironmentType(name='packaging', description="for developers. So that they can test their packaging.", short_name='PCK', chronological_order=3, default_show_sensitive_data=True)
    et4 = EnvironmentType(name='qualification', description="for testers. Unit acceptance testing.", short_name='QUA', chronological_order=5)
    et5 = EnvironmentType(name='recette', description="for testers. Integrated acceptance testing.", short_name='REC', chronological_order=6)
    et6 = EnvironmentType(name='pre-production', description="for the production team.", short_name='PPD', chronological_order=7)
    et7 = EnvironmentType(name='production', description="for the production team.", short_name='PRD', chronological_order=8)
    et8 = EnvironmentType(name='formation', description="for school teachers ;-)", short_name='FOR', chronological_order=9)
    et9 = EnvironmentType(name='référence', description="padua as it used to be", short_name='REF', chronological_order=0)
    et10 = EnvironmentType(name='technique', description="technical testing grounds", short_name='TEC', chronological_order=4)
    et1.save()
    et2.save()
    et3.save()
    et4.save()
    et5.save()
    et6.save()
    et7.save()
    et8.save()
    et9.save()
    et10.save()

    impl_1_1 = ComponentImplementationClass(name='soft1_database_main_oracle', description='Oracle schema for SOFT1 core in a potentially shared instance', implements=l1, technical_description=ImplementationDescription.objects.get(name='oracleschema'))
    impl_2_1 = ComponentImplementationClass(name='soft1_webapp_legacy_was', description='SOFT1 legacy web app in a WebSphere package', implements=l2, technical_description=ImplementationDescription.objects.get(name='wasapplication'))
    impl_2_2 = ComponentImplementationClass(name='soft1_webapp_legacy_jboss', description='SOFT1 legacy web app in a JBoss ear/war package', implements=l2, technical_description=ImplementationDescription.objects.get(name='jbossapplication'))
    impl_3_1 = ComponentImplementationClass(name='soft1_webapp_ee6_was', description='SOFT1 EE6 web app in a WebSphere package', implements=l3, technical_description=ImplementationDescription.objects.get(name='wasapplication'))
    impl_3_2 = ComponentImplementationClass(name='soft1_webapp_ee6_jboss', description='SOFT1 EE6 web app in a JBoss ear/war package', implements=l3, technical_description=ImplementationDescription.objects.get(name='jbossapplication'))
    impl_6_1 = ComponentImplementationClass(name='int_webapp_ee6_was', description='Interfaces EE6 app in a WebSphere package', implements=l6, technical_description=ImplementationDescription.objects.get(name='wasapplication'))
    impl_6_2 = ComponentImplementationClass(name='int_webapp_ee6_jboss', description='Interfaces EE6 app in a JBoss ear/war package', implements=l6, technical_description=ImplementationDescription.objects.get(name='jbossapplication'))
    impl_7_1 = ComponentImplementationClass(name='int_database_main_oracle', description='Oracle schema for integration transit data store in potentially shared instance', implements=l7, technical_description=ImplementationDescription.objects.get(name='oracleschema'))
    impl_8_1 = ComponentImplementationClass(name='int_batch_jqm', description='JQM batch jobs insid a single jar', implements=l8, technical_description=ImplementationDescription.objects.get(name='jqmbatch'))
    impl_1_1.save()
    impl_2_1.save()
    impl_2_2.save()
    impl_3_1.save()
    impl_3_2.save()
    impl_6_1.save()
    impl_6_2.save()
    impl_7_1.save()
    impl_8_1.save()

    et1.implementation_patterns.add(impl_1_1, impl_3_2, impl_7_1)
    et2.implementation_patterns.add(impl_1_1, impl_2_1, impl_3_1)
    et3.implementation_patterns.add(impl_1_1, impl_2_1, impl_3_1)
    et4.implementation_patterns.add(impl_1_1, impl_2_1, impl_3_1)


