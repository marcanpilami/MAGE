# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## MAGE imports
from django.contrib.auth.models import User, Group
from ref.models import EnvironmentType, ImplementationRelationType, ImplementationDescription, AdministrationUnit, \
    Application, LogicalComponent, ComponentImplementationClass, Environment
from django.db.transaction import atomic
from ref.creation import duplicate_envt
from ref.models.acl import AclAuthorization
from ref.models.com import Link


@atomic
def utility_create_meta(project):
    ## Relation classifications
    dt1 = ImplementationRelationType(name='connectedTo')
    dt2 = ImplementationRelationType(name='dependsOn')
    dt1.save()
    dt2.save()

    ######################################################################
    ## Server
    ######################################################################

    ## OS Server
    impl1 = ImplementationDescription.create_or_update('osserver', 'serveur avec un OS', project=project,
                                                       self_description_pattern='"server "|dns', tag='os'). \
        add_field_simple('dns', 'dns d\'administration', widget_row=None). \
        add_field_simple('admin_login', 'login admin', default='root'). \
        add_field_simple('admin_password', 'password admin', sensitive=True)
    impl1.save()

    ## OS account
    impl2 = ImplementationDescription.create_or_update('osaccount', 'compte de connexion au shell',
                                                       self_description_pattern='login', tag='os', project=project). \
        add_field_simple('login', 'login du compte', widget_row=None). \
        add_field_simple('password', 'mot de passe', sensitive=True). \
        add_relationship('server', 'sur le serveur', impl1, dt2, 0, 1)
    impl2.save()


    ######################################################################
    ## Oracle
    ######################################################################

    ## Oracle instance
    impl3 = ImplementationDescription.create_or_update('oracleinstance', 'instance Oracle', project=project,
                                                       self_description_pattern='sid', tag='oracle'). \
        add_field_simple('sid', 'SID of the instance', widget_row=None). \
        add_field_simple('admin_login', 'login DBA', default='scott'). \
        add_field_simple('admin_password', 'mot de passe DBA', default='tiger', sensitive=True). \
        add_field_simple('port', 'port', default=1521). \
        add_field_computed('server_dns', 'DNS serveur', 'server.name'). \
        add_relationship('server', 'serveur', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl3.save()

    ## Oracle schema
    impl4 = ImplementationDescription.create_or_update('oracleschema', 'schéma dans une instance Oracle',
                                                       self_description_pattern='name|" on "|instance.sid',
                                                       tag='oracle', project=project). \
        add_field_simple('name', 'nom', widget_row=None, default="User%E~%%cem~2%s%cem%"). \
        add_field_simple('password', 'password', sensitive=True, default='%e%'). \
        add_field_simple('dns_to_use', 'overload of the server DNS (service address)', label_short='DNS de service',
                         compulsory=False). \
        add_field_simple('service_name_to_use', 'service name', help_text='si null, le SID sera utilisé', default="%E%",
                         compulsory=False). \
        add_field_computed('conn_str', 'sqlplus connection string',
                           'name|"/"|password|"@"|(service_name_to_use?instance.sid)', sensitive=True). \
        add_field_computed('jdbc', 'JDBC connection string',
                           '"jdbc:oracle:thin:@//"|(dns_to_use?instance.server.dns)|":"|instance.port|"/"|(service_name_to_use?instance.sid)'). \
        add_relationship('instance', 'sur instance', impl3, dt2, min_cardinality=1, max_cardinality=1)
    impl4.save()

    ## Oracle package
    impl5 = ImplementationDescription.create_or_update('oraclepackage', 'package dans un schéma Oracle',
                                                       self_description_pattern='name', tag='oracle', project=project). \
        add_field_simple('name', 'package name', widget_row=None). \
        add_relationship('schema', 'schema holding the package', impl4, dt2, min_cardinality=1, max_cardinality=1)
    impl5.save()


    ######################################################################
    ## Message Oriented Middlewares
    ######################################################################

    ## MQ series broker
    impl6 = ImplementationDescription.create_or_update('mqseriesmanager', 'Websphere MQ broker',
                                                       self_description_pattern='name', tag='mq', project=project). \
        add_field_simple('name', 'nom broker', default='QM.%E%', widget_row=None). \
        add_field_simple('port', 'port listener', default='1413+%ciserver.mage_id%'). \
        add_field_simple('admin_channel', 'canal connexion d\'admin', default='SYSTEM.ADMIN.SVRCONN'). \
        add_relationship('server', 'tourne sur le serveur', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl6.save()

    ## MQ series queues configuration
    impl7 = ImplementationDescription.create_or_update('mqseriesparams', 'Websphere MQ broker parameters',
                                                       self_description_pattern='name', tag='mq', project=project). \
        add_field_simple('name', 'parameter set name'). \
        add_relationship('broker', 'target broker', impl6, dt2, min_cardinality=1, max_cardinality=1)
    impl7.save()


    ######################################################################
    ## Batch & JQM
    ######################################################################

    impl8 = ImplementationDescription.create_or_update('applicationfile', 'fichier applicatif',
                                                       self_description_pattern='name', project=project). \
        add_field_simple('name', 'nom fichier', widget_row=None). \
        add_field_simple('path', 'chemin'). \
        add_relationship('belongs_to', 'compte propriétaire', impl2, dt2, min_cardinality=0, max_cardinality=1). \
        add_relationship('server', 'serveur de stockage', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl8.save()

    impl9 = ImplementationDescription.create_or_update('jqmcluster', 'cluster JQM', self_description_pattern='name',
                                                       tag='jqm', project=project). \
        add_field_simple('name', 'cluster name', default='JqmCluster%E~%', widget_row=None). \
        add_relationship('schema', 'Oracle schema of the cluster', impl4, dt2, min_cardinality=0, max_cardinality=1)
    impl9.save()

    impl10 = ImplementationDescription.create_or_update('jqmengine', 'moteur JQM', self_description_pattern='name',
                                                        tag='jqm', project=project). \
        add_field_simple('name', 'node name', default='%ncluster.name%_%ci2cluster.mage_id%', widget_row=None). \
        add_field_simple('port', 'port HTTP', default='1788+%ci2server.mage_id%'). \
        add_field_simple('jmx_registry_port', 'port registry JMX', default='%nport%+1000'). \
        add_field_simple('jmx_server_port', 'port serveur JMX', default='%nport%+1000'). \
        add_field_simple('dl_repo', u'répertoire de stockage des fichiers produits',
                         label_short='dépôt fichiers produits', default="/tmp/%e%/out", compulsory=False,
                         widget_row=None). \
        add_field_simple('job_repo', u'répertoire de stockage des jars utilisateur', label_short='dépôt jobs',
                         default="/tmp/%e%/jars", compulsory=False, widget_row=None). \
        add_relationship('cluster', 'membre du cluster', impl9, dt2, min_cardinality=1, max_cardinality=1). \
        add_relationship('server', 'tourne sur', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl10.save()

    impl11 = ImplementationDescription.create_or_update('jqmbatch', 'batch JQM', self_description_pattern='name',
                                                        tag='jqm', project=project). \
        add_field_simple('name', 'batch name', default='%P1%_%E%_%LC1%', widget_row=None). \
        add_relationship('cluster', 'runs on cluster', impl9, dt2, min_cardinality=1, max_cardinality=1)
    impl11.save()


    ######################################################################
    ## JBoss 7+ (domain mode)
    ######################################################################

    impl12 = ImplementationDescription.create_or_update('jbossdomain', 'domaine JBoss', self_description_pattern='name',
                                                        tag='jboss', project=project). \
        add_field_simple('name', 'domain name', default="JbossCell%cm2%", widget_row=None). \
        add_field_simple('admin_user', 'admin user', default='/'). \
        add_field_simple('admin_password', 'admin password', sensitive=True, default='admin'). \
        add_field_simple('base_http_port', 'HTTP port before shifting', default=8080). \
        add_field_simple('base_https_port', 'HTTPS port before shifting', default=9080). \
        add_field_simple('web_admin_port', 'admin WS port on DC', default=9990). \
        add_field_simple('native_admin_port', 'admin native port on DC', default=9999)
    impl12.save()

    impl13 = ImplementationDescription.create_or_update('jbosshost', u'processus hôte JBoss', project=project,
                                                        self_description_pattern='name', tag='jboss'). \
        add_field_simple('name', 'application name', default='%nserver.dns', widget_row=None). \
        add_field_computed('admin_port', 'admin port', 'domain.native_admin_port'). \
        add_relationship('domain', 'member of domain', impl12, dt2, min_cardinality=1, max_cardinality=1). \
        add_relationship('server', 'run on server', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl13.save()

    impl14 = ImplementationDescription.create_or_update('jbossgroup', u'groupe d\'AS JBoss', project=project,
                                                        self_description_pattern='name', tag='jboss'). \
        add_field_simple('name', 'group name', default='%P1~%%E~%_%cem2%', widget_row=None). \
        add_field_simple('profile', 'profil', default='%E%'). \
        add_field_simple('dedicated_admin_login', u'login admin spécifique', label_short='admin login', default='%e%',
                         compulsory=False, widget_row=None). \
        add_field_simple('dedicated_admin_password', u'mot de passe spécifique', label_short='admin password',
                         default='%e%', compulsory=False, sensitive=True, widget_row=None). \
        add_field_simple('dns_to_use', u'service DNS alias', compulsory=False, widget_row=None). \
        add_field_simple('max_heap_mb', 'Max Heap (Mo)', 384). \
        add_field_simple('max_permgen_mb', 'Max permgen (Mo)', 128). \
        add_field_simple('start_heap_mb', 'Start heap (Mo)', 256). \
        add_field_computed('admin_login', 'admin login', 'dedicated_admin_login?domain.admin_user'). \
        add_field_computed('admin_password', 'admin password', 'dedicated_admin_password?domain.admin_password',
                           sensitive=True). \
        add_relationship('domain', 'member of domain', impl12, dt2, min_cardinality=1, max_cardinality=1)
    impl14.save()

    impl15 = ImplementationDescription.create_or_update('jbossas', u'JVM AS JBoss', self_description_pattern='name',
                                                        tag='jboss', project=project). \
        add_field_simple('name', 'JVM name', default='%ngroup.name%_%ci2group.mage_id%', widget_row=None). \
        add_field_simple('port_shift', 'port shift', default='%cihost.mage_id%*10'). \
        add_field_simple('dns_to_use', 'service DNS entry', compulsory=False, widget_row=None). \
        add_field_computed('http_port', 'actual HTTP port', 'host.domain.base_http_port+port_shift'). \
        add_field_computed('dns', 'actual DNS', 'dns_to_use?group.dns_to_use?host.server.dns'). \
        add_field_computed('group_name', 'inside group', 'group.name'). \
        add_relationship('host', 'runs on host', impl13, dt2, min_cardinality=1, max_cardinality=1). \
        add_relationship('group', 'member of group', impl14, dt2, min_cardinality=1, max_cardinality=1)
    impl15.save()

    impl16 = ImplementationDescription.create_or_update('jbossapplication', 'application JBoss', project=project,
                                                        self_description_pattern='name', tag='jboss'). \
        add_field_simple('name', 'application name', default='%P1%_%E%_%LC1%', widget_row=None). \
        add_field_simple('context_root', 'context root', default='/%lc1%'). \
        add_field_simple('client_url', 'access URL', compulsory=False). \
        add_relationship('group', 'member of cluster', impl14, dt2, min_cardinality=1, max_cardinality=1). \
        add_relationship('schema', 'uses Oracle schema', impl4, dt1, min_cardinality=0, max_cardinality=1). \
        add_relationship('broker', 'uses MQ broker', impl6, dt1, min_cardinality=0, max_cardinality=1). \
        add_field_computed('url', 'end-user URL', '"http://"|client_url?group.dns_to_use')
    impl16.save()


    ######################################################################
    ## WAS 8+ (network deployment mode)
    ######################################################################

    impl17 = ImplementationDescription.create_or_update('wascell', 'WebSphere Application Server Cell',
                                                        self_description_pattern='name', tag='was', project=project). \
        add_field_simple('name', 'cell name'). \
        add_field_simple('manager_port', 'port of network deployment management console', default=9060). \
        add_field_simple('manager_login', 'console admin login', 'admin'). \
        add_field_simple('manager_password', 'console admin password', 'password'). \
        add_field_computed('url', 'manager URL', '"http://"|manager_server.dns|":"|manager_port|"/ibm/console"'). \
        add_relationship('manager_server', 'server holding the deployment manager node', impl1, dt2, min_cardinality=1,
                         max_cardinality=1)
    impl17.save()

    impl18 = ImplementationDescription.create_or_update('wascluster', 'WebSphere Application Server Cluster',
                                                        self_description_pattern='name', tag='was', project=project). \
        add_field_simple('name', 'application name'). \
        add_field_simple('dedicated_admin_user', 'specific account for managing this cluster'). \
        add_field_simple('dedicated_admmin__password', 'specific password'). \
        add_field_computed('admin_login', 'admin login to use', 'dedicated_admin_user?cell.manager_login'). \
        add_field_computed('admin_password', 'admin password to use', 'dedicated_admin_password?cell.manager_password'). \
        add_relationship('cell', 'member of cell', impl17, dt2, min_cardinality=1, max_cardinality=1)
    impl18.save()

    impl19 = ImplementationDescription.create_or_update('wasnode', 'WebSphere Application Server Node',
                                                        self_description_pattern='name', tag='was', project=project). \
        add_field_simple('name', 'node name'). \
        add_relationship('server', 'running on server', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl19.save()

    impl20 = ImplementationDescription.create_or_update('wasas', 'WebSphere Application Server JVM',
                                                        self_description_pattern='name', tag='was', project=project). \
        add_field_simple('name', 'application name'). \
        add_field_simple('http_port', 'HTTP port', 9080). \
        add_field_simple('https_port', 'HTTPS port', 8081). \
        add_field_simple('dns_to_use', 'specific service DNS'). \
        add_relationship('node', 'member of cell', impl19, dt2, min_cardinality=1, max_cardinality=1). \
        add_relationship('cluster', 'member of cell', impl18, dt2, min_cardinality=1, max_cardinality=1)
    impl20.save()

    impl21 = ImplementationDescription.create_or_update('wasapplication', 'Application WebSphere Application Server',
                                                        self_description_pattern='name', tag='was', project=project). \
        add_field_simple('name', 'application name'). \
        add_field_simple('context_root', 'HTTP port', '/'). \
        add_field_simple('client_url', 'service URL'). \
        add_field_computed('url', 'access URL', 'client_url'). \
        add_relationship('cluster', 'member of cell', impl18, dt2, min_cardinality=1, max_cardinality=1)
    impl21.save()


    ######################################################################
    ## MySQL
    ######################################################################

    impl22 = ImplementationDescription.create_or_update('mysqlinstance', 'instance MySQL', project=project,
                                                        self_description_pattern='name', tag='mysql'). \
        add_field_simple('name', 'instance name'). \
        add_field_simple('port', 'remote access port', 3306). \
        add_relationship('server', 'serveur', impl1, dt2, min_cardinality=1, max_cardinality=1)
    impl22.save()

    impl23 = ImplementationDescription.create_or_update('mysqluser', 'compte MySQL', project=project,
                                                        self_description_pattern='name|" on "|instance.name',
                                                        tag='mysql'). \
        add_field_simple('name', 'nom', widget_row=None, default="%e%"). \
        add_field_simple('password', 'password', sensitive=True, default='%e%'). \
        add_relationship('instance', 'instance', impl22, dt2, min_cardinality=1, max_cardinality=1)
    impl23.save()


@atomic
def utility_create_test_instances():
    folder = AdministrationUnit.objects.get(alternate_name_1='ERP')
    folder2 = AdministrationUnit.objects.get(name='Production team environments')

    ## Environments
    e1 = Environment(name='DEV1', description='DEV1', typology=EnvironmentType.objects.get(short_name='DEV'),
                     project=folder)
    e1.save()

    ## OS instances
    i1_1 = ImplementationDescription.class_for_name('osserver')(dns='server1.marsu.net', admin_login='test admin', _folder=folder)
    i1_2 = ImplementationDescription.class_for_name('osserver')(dns='server2.marsu.net', admin_login='test admin', _folder=folder2)

    i2_1 = ImplementationDescription.class_for_name('osaccount')(login='user', password='test', server=i1_1, _folder=folder)
    i2_1.save()

    ## Oracle items
    i3_1 = ImplementationDescription.class_for_name('oracleinstance')(sid='ORAINST1', server=i1_1, admin_login='login',
                                                                      admin_password='toto', _folder=folder)

    i4_1 = ImplementationDescription.class_for_name('oracleschema')(name='schema1', password='pass', instance=i3_1,
                                                                    _env=e1, _cic='soft1_database_main_oracle')
    i4_2 = ImplementationDescription.class_for_name('oracleschema')(name='schema2', password='pass', instance=i3_1,
                                                                    _env=e1, _cic='int_database_main_oracle')
    i4_3 = ImplementationDescription.class_for_name('oracleschema')(name='schema3', password='pass', instance=i3_1,
                                                                    _env=e1)
    i4_1.save()
    i4_2.save()
    i4_3.save()

    ## MQ Series items
    i6_1 = ImplementationDescription.class_for_name('mqseriesmanager')(name='QM.DEV1', _env=e1)

    ## JBoss environment
    i12_1 = ImplementationDescription.class_for_name('jbossdomain')(name=u'domain études', admin_user='admin',
                                                                    admin_password='pass',
                                                                    base_http_port=8080, base_https_port=8081,
                                                                    web_admin_port=9990, native_admin_port=9999,
                                                                    _folder=folder)

    i13_1 = ImplementationDescription.class_for_name('jbosshost')(name=u'jbosshost1.marsu.net', domain=i12_1,
                                                                  server=i1_1, _folder=folder)
    i13_2 = ImplementationDescription.class_for_name('jbosshost')(name=u'jbosshost2.marsu.net', domain=i12_1,
                                                                  server=i1_2, _folder=folder)

    i14_1 = ImplementationDescription.class_for_name('jbossgroup')(domain=i12_1, _env=e1)
    i14_2 = ImplementationDescription.class_for_name('jbossgroup')(domain=i12_1, _env=e1)

    i15_1_1 = ImplementationDescription.class_for_name('jbossas')(host=i13_1, group=i14_1, _env=e1)
    i15_1_2 = ImplementationDescription.class_for_name('jbossas')(host=i13_1, group=i14_1, _env=e1)
    i15_1_3 = ImplementationDescription.class_for_name('jbossas')(host=i13_1, group=i14_1, _env=e1)
    i15_1_4 = ImplementationDescription.class_for_name('jbossas')(host=i13_2, group=i14_1, _env=e1)
    i15_1_5 = ImplementationDescription.class_for_name('jbossas')(host=i13_2, group=i14_1, _env=e1)

    i15_2_1 = ImplementationDescription.class_for_name('jbossas')(host=i13_1, group=i14_2, _env=e1)
    i15_2_2 = ImplementationDescription.class_for_name('jbossas')(host=i13_1, group=i14_2, _env=e1)
    i15_2_3 = ImplementationDescription.class_for_name('jbossas')(host=i13_1, group=i14_2, _env=e1)
    i15_2_4 = ImplementationDescription.class_for_name('jbossas')(host=i13_2, group=i14_2, _env=e1)
    i15_2_5 = ImplementationDescription.class_for_name('jbossas')(host=i13_2, group=i14_2, _env=e1)

    i16_1 = ImplementationDescription.class_for_name('jbossapplication')(context_root='/app1', group=i14_1,
                                                                         _cic='soft1_webapp_ee6_jboss', schema=i4_1,
                                                                         _env=e1)
    i16_1.save()
    i16_2 = ImplementationDescription.class_for_name('jbossapplication')(context_root='/app2', group=i14_2,
                                                                         _cic='soft1_webapp_legacy_jboss', schema=i4_2,
                                                                         _env=e1)
    i16_2.save()
    i16_2 = ImplementationDescription.class_for_name('jbossapplication')(context_root='/app3', group=i14_1, schema=i4_1,
                                                                         _env=e1)
    i16_2.save()

    ## JQM items
    i9_1 = ImplementationDescription.class_for_name('jqmcluster')(schema=i4_3, _env=e1)
    i10_1 = ImplementationDescription.class_for_name('jqmengine')(cluster=i9_1, server=i1_1, _env=e1)
    i11_1 = ImplementationDescription.class_for_name('jqmbatch')(cluster=i9_1, _cic='int_batch_jqm', _env=e1)
    i11_1.save()


def utility_create_admin_structure():
    root = AdministrationUnit.objects.get(name='root')
    p1 = AdministrationUnit(name='SUPER-PROJECT', description='New ERP for FIRM1. A Big Program project.',
                            alternate_name_1='ERP',
                            alternate_name_2='PROJECTCODE', parent=root)
    p1.save()
    p1_1 = AdministrationUnit(name='Project environments',
                              description='All environments not handled by the production team', parent=p1)
    p1_1.save()
    p1_2 = AdministrationUnit(name='Production team environments',
                              description='All environments handled by the production team', parent=p1)
    p1_2.save()
    p1_3 = AdministrationUnit(name='Externalized environments', description='Delegated to maintenance team',
                              parent=p1_2, block_inheritance=True)
    p1_3.save()

    p2 = AdministrationUnit(name='Side project', description='Small side project to test mysql',
                            alternate_name_1='TSTMSQL', parent=root)
    p2.save()


@atomic
def utility_create_logical():
    a1 = Application(name='Soft1', description='Super New ERP', alternate_name_1="SFT1",
                     project=AdministrationUnit.objects.get(name='SUPER-PROJECT'))
    a1.save()
    a2 = Application(name='Interfaces',
                     description='developments to interface Soft1 with the rest of the FIRM1 systems',
                     alternate_name_1="SFT2", project=AdministrationUnit.objects.get(name='SUPER-PROJECT'))
    a2.save()

    l1 = LogicalComponent(name='main database', description="relational database containing the core Soft1 data",
                          application=a1, ref1='pua')
    l1.save()
    l2 = LogicalComponent(name='web application STRUTS', description="The old Java STRUTS application", application=a1,
                          ref1='pua')
    l2.save()
    l3 = LogicalComponent(name='web application EE6', description="The new EE6 application", application=a1, ref1='pu6')
    l3.save()
    l4 = LogicalComponent(name='web application container', description="Container for EE6 applications",
                          application=a1, scm_trackable=False)
    l4.save()
    # l5 = LogicalComponent(name='Interfaces queue broker config', description="description", application=a2)
    # l5.save()
    l6 = LogicalComponent(name='Interfaces EE6 application', description="description", application=a2)
    l6.save()
    l7 = LogicalComponent(name='main database',
                          description="relational database for the staging needs of the interfaces", application=a2,
                          ref1='int')
    l7.save()
    l8 = LogicalComponent(name='batch jobs', description="batch jobs from the interfaces", application=a2, ref1='int')
    l8.save()

    et1 = EnvironmentType(name='development', description="for developers. No admin except for middlewares.",
                          short_name='DEV', chronological_order=1, default_show_sensitive_data=True)
    et2 = EnvironmentType(name='test', description="for developers. So that they can test their production.",
                          short_name='TST', chronological_order=2, default_show_sensitive_data=True)
    et3 = EnvironmentType(name='packaging', description="for developers. So that they can test their packaging.",
                          short_name='PCK', chronological_order=3, default_show_sensitive_data=True)
    et4 = EnvironmentType(name='qualification', description="for testers. Unit acceptance testing.", short_name='QUA',
                          chronological_order=5)
    et5 = EnvironmentType(name='recette', description="for testers. Integrated acceptance testing.", short_name='REC',
                          chronological_order=6)
    et6 = EnvironmentType(name='pre-production', description="for the production team.", short_name='PPD',
                          chronological_order=7)
    et7 = EnvironmentType(name='production', description="for the production team.", short_name='PRD',
                          chronological_order=8)
    et8 = EnvironmentType(name='formation', description="for school teachers ;-)", short_name='FOR',
                          chronological_order=9)
    et9 = EnvironmentType(name='référence', description="padua as it used to be", short_name='REF',
                          chronological_order=0)
    et10 = EnvironmentType(name='technique', description="technical testing grounds", short_name='TEC',
                           chronological_order=4)
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

    impl_1_1 = ComponentImplementationClass(name='soft1_database_main_oracle',
                                            description='Oracle schema for SOFT1 core in a potentially shared instance',
                                            implements=l1, technical_description=ImplementationDescription.objects.get(
            name='oracleschema'))
    impl_2_1 = ComponentImplementationClass(name='soft1_webapp_legacy_was',
                                            description='SOFT1 legacy web app in a WebSphere package', implements=l2,
                                            technical_description=ImplementationDescription.objects.get(
                                                name='wasapplication'))
    impl_2_2 = ComponentImplementationClass(name='soft1_webapp_legacy_jboss',
                                            description='SOFT1 legacy web app in a JBoss ear/war package',
                                            implements=l2, technical_description=ImplementationDescription.objects.get(
            name='jbossapplication'))
    impl_3_1 = ComponentImplementationClass(name='soft1_webapp_ee6_was',
                                            description='SOFT1 EE6 web app in a WebSphere package', implements=l3,
                                            technical_description=ImplementationDescription.objects.get(
                                                name='wasapplication'))
    impl_3_2 = ComponentImplementationClass(name='soft1_webapp_ee6_jboss',
                                            description='SOFT1 EE6 web app in a JBoss ear/war package', implements=l3,
                                            technical_description=ImplementationDescription.objects.get(
                                                name='jbossapplication'))
    impl_6_1 = ComponentImplementationClass(name='int_webapp_ee6_was',
                                            description='Interfaces EE6 app in a WebSphere package', implements=l6,
                                            technical_description=ImplementationDescription.objects.get(
                                                name='wasapplication'))
    impl_6_2 = ComponentImplementationClass(name='int_webapp_ee6_jboss',
                                            description='Interfaces EE6 app in a JBoss ear/war package', implements=l6,
                                            technical_description=ImplementationDescription.objects.get(
                                                name='jbossapplication'))
    impl_7_1 = ComponentImplementationClass(name='int_database_main_oracle',
                                            description='Oracle schema for integration transit data store in potentially shared instance',
                                            implements=l7, technical_description=ImplementationDescription.objects.get(
            name='oracleschema'))
    impl_7_2 = ComponentImplementationClass(name='int_database_main_mysql_dedicated',
                                            description='MySQL schema for integration transit data store in dedicated instance',
                                            implements=l7, technical_description=ImplementationDescription.objects.get(
            name='mysqluser'))
    impl_8_1 = ComponentImplementationClass(name='int_batch_jqm', description='JQM batch jobs insid a single jar',
                                            implements=l8, technical_description=ImplementationDescription.objects.get(
            name='jqmbatch'))
    impl_1_1.save()
    impl_2_1.save()
    impl_2_2.save()
    impl_3_1.save()
    impl_3_2.save()
    impl_6_1.save()
    impl_6_2.save()
    impl_7_1.save()
    impl_7_2.save()
    impl_8_1.save()

    et1.implementation_patterns.add(impl_1_1, impl_3_2, impl_7_1)
    et2.implementation_patterns.add(impl_1_1, impl_2_1, impl_3_1)
    et3.implementation_patterns.add(impl_1_1, impl_2_1, impl_3_1)
    et4.implementation_patterns.add(impl_1_1, impl_2_1, impl_3_1)


def utility_create_test_users():
    a = User.objects.create_superuser('a', 'a@o.fr', 'a')
    b = User.objects.create_user('b', 'b@o.fr', 'b')
    c = User.objects.create_user('c', 'c@o.fr', 'c')

    g1 = Group(name='api')
    g1.save()

    g2 = Group(name='dev')
    g2.save()

    g3 = Group(name='ro')
    g3.save()
    AclAuthorization(target=AdministrationUnit.objects.get(name='root'), codename='read_folder', group=g3).save()
    AclAuthorization(target=AdministrationUnit.objects.get(name='root'), codename='list_envt', group=g3).save()
    AclAuthorization(target=AdministrationUnit.objects.get(name='root'), codename='read_envt', group=g3).save()

    g4 = Group(name='rw')
    g4.save()

    g5 = Group(name='admin')
    g5.save()

    b.groups.add(g3)


@atomic
def create_full_test_data():
    utility_create_admin_structure()
    utility_create_meta(AdministrationUnit.objects.get(name='SUPER-PROJECT'))
    utility_create_logical()
    utility_create_test_instances()
    utility_create_test_users()

    dev2 = duplicate_envt("DEV1", "DEV2")
    tec1 = duplicate_envt("DEV1", "TEC1")
    tec2 = duplicate_envt("DEV1", "TEC2")
    qua1 = duplicate_envt("DEV1", "QUA1")
    rec1 = duplicate_envt("DEV1", "REC1")
    for1 = duplicate_envt("DEV1", "FOR1")

    dev2.managed = False
    dev2.save()

    l = Link(url="http://www.marsupilami.com", legend='Link of use for your users, or important message',
             color="#1B58B8")
    l.save()
    l = Link(url="http://www.marsupilami.com", legend='Second link of use for your users, or important message',
             color="#1B58B8")
    l.save()
