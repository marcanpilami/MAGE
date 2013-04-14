# coding: utf-8

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from scm.models import InstallableSet, InstallableItem, InstallationMethod, \
    LogicalComponentVersion, Delivery
from ref.models import Application, LogicalComponent, \
    ComponentImplementationClass, EnvironmentType, Environment
from cpn.models import OsServer, OracleInstance, OracleSchema
from cpn.tests import TestHelper, utility_create_test_envt 
from install import install_iset_envt
from scm.exceptions import MageScmFailedEnvironmentDependencyCheck


def create_test_is():
    res = []
    utility_create_test_envt(1)
    ref = TestHelper()
    
    # Versions (independent of II)
    rdbms1_v1 = LogicalComponentVersion(version='v1', logical_component=ref.logical_rdbms_module1)
    rdbms1_v1.save()
    rdbms1_v2 = LogicalComponentVersion(version='v1.2', logical_component=ref.logical_rdbms_module1)
    rdbms1_v2.save()
    rdbms1_v3 = LogicalComponentVersion(version='v1.3', logical_component=ref.logical_rdbms_module1)
    rdbms1_v3.save()
    
    rdbms2_v1 = LogicalComponentVersion(version='a', logical_component=ref.logical_rdbms_module2)
    rdbms2_v1.save()
    rdbms2_v2 = LogicalComponentVersion(version='b', logical_component=ref.logical_rdbms_module2)
    rdbms2_v2.save()
    rdbms2_v3 = LogicalComponentVersion(version='c', logical_component=ref.logical_rdbms_module2)
    rdbms2_v3.save()
    rdbms2_v4 = LogicalComponentVersion(version='d', logical_component=ref.logical_rdbms_module2)
    rdbms2_v4.save()
    rdbms2_v5 = LogicalComponentVersion(version='e', logical_component=ref.logical_rdbms_module2)
    rdbms2_v5.save()
    rdbms2_v6 = LogicalComponentVersion(version='f', logical_component=ref.logical_rdbms_module2)
    rdbms2_v6.save()
    
    # Installation methods (independent of IS)
    rdbms1_meth1 = InstallationMethod(name='Scripts SQL Oracle', halts_service=True)
    rdbms1_meth1.save()
    rdbms1_meth1.method_compatible_with.add(ref.cic_rdbms_module1_oracle_mut, ref.cic_rdbms_module2_oracle_mut)
    rdbms1_meth2 = InstallationMethod(name='Scripts SQL Postgresql', halts_service=True)
    rdbms1_meth2.save()
    rdbms1_meth2.method_compatible_with.add(ref.cic_rdbms_module1_postgres_dedicated)
    
    # First IS
    is1 = Delivery(name='SYSTEM1_INIT', description='Initial delivery')
    is1.save()
 
    is1_ii1 = InstallableItem(what_is_installed=rdbms1_v1, belongs_to_set=is1, is_full=True, data_loss=True)
    is1_ii1.save()
    is1_ii1.how_to_install.add(rdbms1_meth1)
    is1_ii2 = InstallableItem(what_is_installed=rdbms2_v1, belongs_to_set=is1, is_full=True, data_loss=True)
    is1_ii2.save()
    is1_ii2.how_to_install.add(rdbms1_meth1)
    
    res.append(is1)
    
    # Second IS
    is2 = Delivery(name='SYSTEM1_2', description='Solves all issues. Once again.')
    is2.save()
 
    is2_ii1 = InstallableItem(what_is_installed=rdbms1_v2, belongs_to_set=is2)
    is2_ii1.save()
    is2_ii1.how_to_install.add(rdbms1_meth1)
    is2_ii2 = InstallableItem(what_is_installed=rdbms2_v2, belongs_to_set=is2)
    is2_ii2.save()
    is2_ii2.how_to_install.add(rdbms1_meth1)
    
    is2_ii1.dependsOn(rdbms1_v1, '==')
    is2_ii2.dependsOn(rdbms2_v1, '==')
    
    res.append(is2)
    
    
    # Third IS
    is3 = Delivery(name='SYSTEM1_3', description='blah.')
    is3.save()
 
    is3_ii1 = InstallableItem(what_is_installed=rdbms2_v3, belongs_to_set=is3)
    is3_ii1.save()
    is3_ii1.how_to_install.add(rdbms1_meth1)
    
    is3_ii1.dependsOn(rdbms2_v1, '==')
    is3_ii1.dependsOn(rdbms1_v1, '>=')
    
    res.append(is3)
    
    # Fourth IS
    is4 = Delivery(name='SYSTEM1_4', description='blah.')
    is4.save()
 
    is4_ii1 = InstallableItem(what_is_installed=rdbms2_v4, belongs_to_set=is4)
    is4_ii1.save()
    is4_ii1.how_to_install.add(rdbms1_meth1)
    
    is4_ii1.dependsOn(rdbms2_v3, '>=')
    is4_ii1.dependsOn(rdbms1_v2, '==')
    
    res.append(is4)
    
    # Fifth IS
    is5 = Delivery(name='SYSTEM1_5', description='blah.')
    is5.save()
 
    is5_ii1 = InstallableItem(what_is_installed=rdbms2_v5, belongs_to_set=is5)
    is5_ii1.save()
    is5_ii1.how_to_install.add(rdbms1_meth1)
    
    is5_ii1.dependsOn(rdbms2_v1, '>=')
    is5_ii1.dependsOn(rdbms2_v3, '<=')
    
    is5_ii1.dependsOn(rdbms1_v2, '==')
    
    res.append(is5)
    
    # Sixth IS: same version - different deps
    is6 = Delivery(name='SYSTEM1_6', description='blah.')
    is6.save()
 
    is6_ii1 = InstallableItem(what_is_installed=rdbms2_v5, belongs_to_set=is6)
    is6_ii1.save()
    is6_ii1.how_to_install.add(rdbms1_meth1)
    
    is6_ii1.dependsOn(rdbms2_v4, '==')
    is6_ii1.dependsOn(rdbms1_v2, '==')
    
    res.append(is6)
    
    # Seventh IS: final one - will not be applied, just to keep something to be applied for manual tests
    is7 = Delivery(name='SYSTEM1_7', description='blah.')
    is7.save()
 
    is7_ii1 = InstallableItem(what_is_installed=rdbms2_v6, belongs_to_set=is7)
    is7_ii1.save()
    is7_ii1.how_to_install.add(rdbms1_meth1)
    
    is7_ii1.dependsOn(rdbms2_v5, '==')
    is7_ii1.dependsOn(rdbms1_v2, '==')
    
    res.append(is6)
    
    return res
    
class SimpleTest(TestCase):
     
    def test_create(self):
        create_test_is()
        self.assertLess(0, InstallableItem.objects.count())

    def test_install1(self):
        is_list = create_test_is()
        ref = TestHelper()
        
        install_iset_envt(is_list[0], ref.envt_prd1)
        self.assertEqual(ref.ci_ora_1.version, 'v1')
        
        install_iset_envt(is_list[1], ref.envt_prd1)
        self.assertEqual(ref.ci_ora_1.version, 'v1.2')
    
    def test_ver_compare(self):
        create_test_is()
        
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
        is_list = create_test_is()
        ref = TestHelper()
        
        # No version data -> error
        with self.assertRaises(MageScmFailedEnvironmentDependencyCheck):
            is_list[2].check_prerequisites('PRD1')
        
        # v1/v1 => both prereqs OK
        install_iset_envt(is_list[0], ref.envt_prd1)
        self.assertTrue(is_list[2].check_prerequisites('PRD1'))
        
        # v2/v2 => first prereq KO
        install_iset_envt(is_list[1], ref.envt_prd1)
        with self.assertRaises(MageScmFailedEnvironmentDependencyCheck):
            is_list[2].check_prerequisites('PRD1')
            
        # v2/v3
        install_iset_envt(is_list[2], ref.envt_prd1)
        self.assertTrue(is_list[4].check_prerequisites('PRD1'))

        # v2/v4
        self.assertTrue(is_list[3].check_prerequisites('PRD1'))
        install_iset_envt(is_list[3], ref.envt_prd1)
        with self.assertRaises(MageScmFailedEnvironmentDependencyCheck):
            is_list[4].check_prerequisites('PRD1') # V4 instead of [1,3]

        # v2/v5  
        self.assertTrue(is_list[5].check_prerequisites('PRD1'))
        install_iset_envt(is_list[5], ref.envt_prd1)
              
