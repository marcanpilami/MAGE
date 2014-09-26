# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

## Django imports
from django.utils.timezone import now
from django.test import TestCase

## MAGE imports
from scm.models import InstallableItem, LogicalComponentVersion, Installation
from install import install_iset_envt
from scm.exceptions import MageScmFailedEnvironmentDependencyCheck
from scm.backup import register_backup
from scm.install import install_ii_single_target_envt
from ref.models.parameters import setOrCreateParam
from scm.demo_items import create_test_is
from ref.models.instances import Environment



class SimpleTest(TestCase):
    def setUp(self):
        self.is_list = create_test_is()
        self.e = Environment.objects.get(name='QUA1')
        self.ci_app1 = self.e.component_instances.get(instanciates__name='soft1_database_main_oracle')
        self.ci_app2 = self.e.component_instances.get(instanciates__name='int_database_main_oracle')

    def test_create(self):
        self.assertLess(0, InstallableItem.objects.count())

    def test_install1(self):
        install_iset_envt(self.is_list[0], self.e)
        self.assertEqual(self.ci_app1.version, 'v1')

        install_iset_envt(self.is_list[1], self.e)
        self.assertEqual(self.ci_app1.version, 'v1.2')

    def test_ver_compare(self):
        rdbms1_v1 = LogicalComponentVersion.objects.get(version='v1')
        rdbms1_v2 = LogicalComponentVersion.objects.get(version='v1.2')
        rdbms2_v1 = LogicalComponentVersion.objects.get(version='a')
        rdbms2_v2 = LogicalComponentVersion.objects.get(version='b')
        rdbms2_v3 = LogicalComponentVersion.objects.get(version='c')

        self.assertEqual(rdbms2_v3.compare(rdbms1_v1), 1)
        self.assertEqual(rdbms1_v1.compare(rdbms2_v3), -1)
        self.assertEqual(rdbms2_v3.compare(rdbms2_v1), 1)
        self.assertEqual(rdbms2_v3.compare(rdbms1_v2), 0)
        self.assertEqual(rdbms2_v3.compare(rdbms2_v2), 0)


    def test_dep(self):
        # No version data -> error
        with self.assertRaises(MageScmFailedEnvironmentDependencyCheck):
            self.is_list[2].check_prerequisites('QUA1')

        # v1/v1 => both prereqs OK
        install_iset_envt(self.is_list[0], self.e)
        self.assertTrue(self.is_list[2].check_prerequisites('QUA1'))

        # v2/v2 => first prereq KO
        install_iset_envt(self.is_list[1], self.e)
        with self.assertRaises(MageScmFailedEnvironmentDependencyCheck):
            self.is_list[2].check_prerequisites('QUA1')

        # v2/v3
        install_iset_envt(self.is_list[2], self.e, force_prereqs=True)
        self.assertTrue(self.is_list[4].check_prerequisites('QUA1'))

        # v2/v4
        self.assertTrue(self.is_list[3].check_prerequisites('QUA1'))
        install_iset_envt(self.is_list[3], self.e)
        with self.assertRaises(MageScmFailedEnvironmentDependencyCheck):
            self.is_list[4].check_prerequisites('QUA1') # V4 instead of [1,3]

        # v2/v5
        self.assertTrue(self.is_list[5].check_prerequisites('QUA1'))
        install_iset_envt(self.is_list[5], self.e)

    def test_backup(self):
        bs = register_backup('QUA1', now(), None, *self.e.component_instances.all(), description="marsu")
        install_iset_envt(bs, Environment.objects.get(name='TEC1'))

    def test_merge(self):
        iset = self.is_list[0]
        ii1 = iset.set_content.all()[0]
        ii2 = iset.set_content.all()[1]

        install_ii_single_target_envt(ii1, self.ci_app1, self.e)
        self.assertEqual(self.ci_app1.version, 'v1')

        install_ii_single_target_envt(ii2, self.ci_app2, self.e)
        self.assertEqual(self.ci_app2.version, 'a')

        installs = Installation.objects.all().count()
        self.assertEqual(1, installs)

    def test_not_merge(self):
        setOrCreateParam(key=u'APPLY_MERGE_LIMIT', value=u'0') ## Disable merge

        iset = self.is_list[0]
        ii1 = iset.set_content.all()[0]
        ii2 = iset.set_content.all()[1]

        install_ii_single_target_envt(ii1, self.ci_app1, self.e)
        self.assertEqual(self.ci_app1.version, 'v1')

        install_ii_single_target_envt(ii2, self.ci_app2, self.e)
        self.assertEqual(self.ci_app2.version, 'a')

        installs = Installation.objects.all().count()
        self.assertEqual(2, installs)
