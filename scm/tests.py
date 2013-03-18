"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from scm.models import InstallableSet, InstallableItem, InstallationMethod,\
    LogicalComponentVersion, Delivery
from ref.models import Application, LogicalComponent, \
    ComponentImplementationClass, EnvironmentType, Environment
from cpn.models import UnixServer, OracleInstance, OracleSchema
from cpn.tests import TestHelper, utility_create_test_envt 
from install import install_iset_envt


def create_test_is():
    res = []
    utility_create_test_envt(1)
    ref = TestHelper()
    
    # Versions (independent of II)
    rdbms1_v1 = LogicalComponentVersion(version = 'v1', logical_component = ref.logical_rdbms_module1)
    rdbms1_v1.save()
    rdbms1_v2 = LogicalComponentVersion(version = 'v1.2', logical_component = ref.logical_rdbms_module1)
    rdbms1_v2.save()
    
    rdbms2_v1 = LogicalComponentVersion(version = 'a', logical_component = ref.logical_rdbms_module2)
    rdbms2_v1.save()
    rdbms2_v2 = LogicalComponentVersion(version = 'b', logical_component = ref.logical_rdbms_module2)
    rdbms2_v2.save()
    
    # Installation methods (independent of IS)
    rdbms1_meth1 = InstallationMethod(script_to_run = 'none', halts_service = True)
    rdbms1_meth1.save()
    rdbms1_meth1.method_compatible_with.add(ref.cic_rdbms_module1_oracle_mut, ref.cic_rdbms_module2_oracle_mut)
    
    # First IS
    is1 = Delivery(name='SYSTEM1_23B2', description='Solves all issues. Ever.')
    is1.save()
 
    is1_ii1 = InstallableItem(what_is_installed = rdbms1_v1, how_to_install = rdbms1_meth1, belongs_to_set = is1)
    is1_ii1.save()
    
    res.append(is1)
    
    # Second IS
    is2 = Delivery(name='SYSTEM1_23B2.2', description='Solves all issues. Once again.')
    is2.save()
 
    is2_ii1 = InstallableItem(what_is_installed = rdbms1_v2, how_to_install = rdbms1_meth1, belongs_to_set = is2)
    is2_ii1.save()
    is2_ii2 = InstallableItem(what_is_installed = rdbms2_v1, how_to_install = rdbms1_meth1, belongs_to_set = is2)
    is2_ii2.save()
    
    res.append(is2)
    
    
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
        