# coding: utf-8
from ref.demo_items import create_full_test_data
from scm.models import LogicalComponentVersion, InstallationMethod, Delivery, \
    InstallableItem, ComponentInstanceConfiguration, InstallableSet, Installation
from ref.models import LogicalComponent, ComponentImplementationClass, ImplementationDescription , ComponentInstance, \
    Environment
from django.db.transaction import atomic
from django.utils import timezone

@atomic
def create_test_is():
    res = []
    create_full_test_data()

    lc_rdbms_module1 = LogicalComponent.objects.get(name="main database", application__alternate_name_1='SFT1')
    lc_rdbms_module2 = LogicalComponent.objects.get(name="main database", application__alternate_name_1='SFT2')

    # Versions (independent of II)
    rdbms1_v1 = LogicalComponentVersion(version='v1', logical_component=lc_rdbms_module1)
    rdbms1_v1.save()
    rdbms1_v2 = LogicalComponentVersion(version='v1.2', logical_component=lc_rdbms_module1)
    rdbms1_v2.save()
    rdbms1_v3 = LogicalComponentVersion(version='v1.3', logical_component=lc_rdbms_module1)
    rdbms1_v3.save()
    rdbms1_vr1 = LogicalComponentVersion(version='v-1', logical_component=lc_rdbms_module1)
    rdbms1_vr1.save()
    rdbms1_vr2 = LogicalComponentVersion(version='v-2', logical_component=lc_rdbms_module1)
    rdbms1_vr2.save()
    rdbms1_vr3 = LogicalComponentVersion(version='v-3', logical_component=lc_rdbms_module1)
    rdbms1_vr3.save()

    rdbms2_v1 = LogicalComponentVersion(version='a', logical_component=lc_rdbms_module2)
    rdbms2_v1.save()
    rdbms2_v2 = LogicalComponentVersion(version='b', logical_component=lc_rdbms_module2)
    rdbms2_v2.save()
    rdbms2_v3 = LogicalComponentVersion(version='c', logical_component=lc_rdbms_module2)
    rdbms2_v3.save()
    rdbms2_v4 = LogicalComponentVersion(version='d', logical_component=lc_rdbms_module2)
    rdbms2_v4.save()
    rdbms2_v5 = LogicalComponentVersion(version='e', logical_component=lc_rdbms_module2)
    rdbms2_v5.save()
    rdbms2_v6 = LogicalComponentVersion(version='f', logical_component=lc_rdbms_module2)
    rdbms2_v6.save()

    project1 = rdbms1_v1.logical_component.application.project

    # Installation methods (independent of IS)
    rdbms1_meth1 = InstallationMethod(name='Scripts SQL Oracle v1.0', halts_service=True)
    rdbms1_meth1.save()
    rdbms1_meth1.method_compatible_with.add(ComponentImplementationClass.objects.get(name='soft1_database_main_oracle'), ComponentImplementationClass.objects.get(name='int_database_main_oracle'))
    rdbms1_meth2 = InstallationMethod(name='Scripts SQL MySQL v1.0', halts_service=True)
    rdbms1_meth2.save()
    rdbms1_meth2.method_compatible_with.add(ComponentImplementationClass.objects.get(name='int_database_main_mysql_dedicated'))

    # First IS
    is1 = Delivery(name='SYSTEM1_INIT', description='Initial delivery', project=project1)
    is1.save()

    is1_ii1 = InstallableItem(what_is_installed=rdbms1_v1, belongs_to_set=is1, is_full=True, data_loss=True)
    is1_ii1.save()
    is1_ii1.how_to_install.add(rdbms1_meth1)
    is1_ii2 = InstallableItem(what_is_installed=rdbms2_v1, belongs_to_set=is1, is_full=True, data_loss=True)
    is1_ii2.save()
    is1_ii2.how_to_install.add(rdbms1_meth1)

    res.append(is1)

    # Second IS
    is2 = Delivery(name='SYSTEM1_2', description='Solves all issues. Once again.', project=project1)
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
    is3 = Delivery(name='SYSTEM1_3', description='blah.', project=project1)
    is3.save()

    is3_ii1 = InstallableItem(what_is_installed=rdbms2_v3, belongs_to_set=is3)
    is3_ii1.save()
    is3_ii1.how_to_install.add(rdbms1_meth1)

    is3_ii1.dependsOn(rdbms2_v1, '==')
    is3_ii1.dependsOn(rdbms1_v1, '>=')

    res.append(is3)

    # Fourth IS
    is4 = Delivery(name='SYSTEM1_4', description='blah.', project=project1)
    is4.save()

    is4_ii1 = InstallableItem(what_is_installed=rdbms2_v4, belongs_to_set=is4)
    is4_ii1.save()
    is4_ii1.how_to_install.add(rdbms1_meth1)

    is4_ii1.dependsOn(rdbms2_v3, '>=')
    is4_ii1.dependsOn(rdbms1_v2, '==')

    res.append(is4)

    # Fifth IS
    is5 = Delivery(name='SYSTEM1_5', description='blah.', project=project1)
    is5.save()

    is5_ii1 = InstallableItem(what_is_installed=rdbms2_v5, belongs_to_set=is5)
    is5_ii1.save()
    is5_ii1.how_to_install.add(rdbms1_meth1)

    is5_ii1.dependsOn(rdbms2_v1, '>=')
    is5_ii1.dependsOn(rdbms2_v3, '<=')

    is5_ii1.dependsOn(rdbms1_v2, '==')

    res.append(is5)

    # Sixth IS: same version - different deps
    is6 = Delivery(name='SYSTEM1_6', description='blah.', project=project1)
    is6.save()

    is6_ii1 = InstallableItem(what_is_installed=rdbms2_v5, belongs_to_set=is6)
    is6_ii1.save()
    is6_ii1.how_to_install.add(rdbms1_meth1)

    is6_ii1.dependsOn(rdbms2_v4, '==')
    is6_ii1.dependsOn(rdbms1_v2, '==')

    res.append(is6)

    # Seventh IS: final one - will not be applied, just to keep something to be applied for manual tests
    is7 = Delivery(name='SYSTEM1_7', description='blah.', project=project1)
    is7.save()

    is7_ii1 = InstallableItem(what_is_installed=rdbms2_v6, belongs_to_set=is7)
    is7_ii1.save()
    is7_ii1.how_to_install.add(rdbms1_meth1)

    is7_ii1.dependsOn(rdbms2_v5, '==')
    is7_ii1.dependsOn(rdbms1_v2, '==')

    res.append(is6)

    # Reverse chain IS 1 (version -1)
    isr1 = Delivery(name='SYSTEM1_RV1', description='blah.', project=project1)
    isr1.save()

    isr1_ii1 = InstallableItem(what_is_installed=rdbms1_vr1, belongs_to_set=isr1)
    isr1_ii1.save()
    isr1_ii1.how_to_install.add(rdbms1_meth1)

    isr1_ii1.dependsOn(rdbms1_v1, '<=')

    res.append(isr1)

    # Reverse chain IS 2 (version -2)
    isr2 = Delivery(name='SYSTEM1_RV2', description='blah.', project=project1)
    isr2.save()

    isr2_ii1 = InstallableItem(what_is_installed=rdbms1_vr2, belongs_to_set=isr2)
    isr2_ii1.save()
    isr2_ii1.how_to_install.add(rdbms1_meth1)

    isr2_ii1.dependsOn(rdbms1_vr1, '<=')

    # Reverse chain IS 3 (version -3)
    isr3 = Delivery(name='SYSTEM1_RV3', description='blah.', project=project1)
    isr3.save()

    isr3_ii1 = InstallableItem(what_is_installed=rdbms1_vr3, belongs_to_set=isr3)
    isr3_ii1.save()
    isr3_ii1.how_to_install.add(rdbms1_meth1)

    isr2_ii1.dependsOn(rdbms1_vr2, '>=')


    return res
