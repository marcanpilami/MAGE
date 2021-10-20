# coding: utf-8
from ref.demo_items import create_full_test_data
from scm.models import LogicalComponentVersion, InstallationMethod, Delivery, \
    InstallableItem
from ref.models import LogicalComponent, ComponentImplementationClass
from django.db.transaction import atomic

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

    # Installation methods (independent of IS)
    rdbms1_meth1 = InstallationMethod(name='Scripts SQL Oracle v1.0', halts_service=True)
    rdbms1_meth1.save()
    rdbms1_meth1.method_compatible_with.add(ComponentImplementationClass.objects.get(name='soft1_database_main_oracle'), ComponentImplementationClass.objects.get(name='int_database_main_oracle'))
    rdbms1_meth2 = InstallationMethod(name='Scripts SQL MySQL v1.0', halts_service=True)
    rdbms1_meth2.save()
    rdbms1_meth2.method_compatible_with.add(ComponentImplementationClass.objects.get(name='int_database_main_mysql_dedicated'))

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

    # Reverse chain IS 1 (version -1)
    isr1 = Delivery(name='SYSTEM1_RV1', description='blah.')
    isr1.save()

    isr1_ii1 = InstallableItem(what_is_installed=rdbms1_vr1, belongs_to_set=isr1)
    isr1_ii1.save()
    isr1_ii1.how_to_install.add(rdbms1_meth1)

    isr1_ii1.dependsOn(rdbms1_v1, '<=')

    res.append(isr1)

    # Reverse chain IS 2 (version -2)
    isr2 = Delivery(name='SYSTEM1_RV2', description='blah.')
    isr2.save()

    isr2_ii1 = InstallableItem(what_is_installed=rdbms1_vr2, belongs_to_set=isr2)
    isr2_ii1.save()
    isr2_ii1.how_to_install.add(rdbms1_meth1)

    isr2_ii1.dependsOn(rdbms1_vr1, '<=')

    # Reverse chain IS 3 (version -3)
    isr3 = Delivery(name='SYSTEM1_RV3', description='blah.')
    isr3.save()

    isr3_ii1 = InstallableItem(what_is_installed=rdbms1_vr3, belongs_to_set=isr3)
    isr3_ii1.save()
    isr3_ii1.how_to_install.add(rdbms1_meth1)

    isr2_ii1.dependsOn(rdbms1_vr2, '>=')
    
    ########################### Multiproject mode ###########################

    lc_rdbms_module3 = LogicalComponent.objects.get(name="main database", application__alternate_name_1='SFT3')
    lc_rdbms_module4 = LogicalComponent.objects.get(name="main database", application__alternate_name_1='SFT4')

    # Versions (independent of II)
    rdbms3_v1 = LogicalComponentVersion(version='v1', logical_component=lc_rdbms_module3)
    rdbms3_v1.save()
    rdbms3_v2 = LogicalComponentVersion(version='v1.2', logical_component=lc_rdbms_module3)
    rdbms3_v2.save()
    rdbms3_v3 = LogicalComponentVersion(version='v1.3', logical_component=lc_rdbms_module3)
    rdbms3_v3.save()
    rdbms3_vr1 = LogicalComponentVersion(version='v-1', logical_component=lc_rdbms_module3)
    rdbms3_vr1.save()
    rdbms3_vr2 = LogicalComponentVersion(version='v-2', logical_component=lc_rdbms_module3)
    rdbms3_vr2.save()
    rdbms3_vr3 = LogicalComponentVersion(version='v-3', logical_component=lc_rdbms_module3)
    rdbms3_vr3.save()

    rdbms4_v1 = LogicalComponentVersion(version='a', logical_component=lc_rdbms_module4)
    rdbms4_v1.save()
    rdbms4_v2 = LogicalComponentVersion(version='b', logical_component=lc_rdbms_module4)
    rdbms4_v2.save()
    rdbms4_v3 = LogicalComponentVersion(version='c', logical_component=lc_rdbms_module4)
    rdbms4_v3.save()
    rdbms4_v4 = LogicalComponentVersion(version='d', logical_component=lc_rdbms_module4)
    rdbms4_v4.save()
    rdbms4_v5 = LogicalComponentVersion(version='e', logical_component=lc_rdbms_module4)
    rdbms4_v5.save()
    rdbms4_v6 = LogicalComponentVersion(version='f', logical_component=lc_rdbms_module4)
    rdbms4_v6.save()

    # Installation methods (independent of IS)
    rdbms3_meth1 = InstallationMethod(name='Scripts SQL Oracle v1.0', halts_service=True)
    rdbms3_meth1.save()
    rdbms3_meth1.method_compatible_with.add(ComponentImplementationClass.objects.get(name='soft1_database_main_oracle'),
                                            ComponentImplementationClass.objects.get(name='int_database_main_oracle'))
    rdbms3_meth2 = InstallationMethod(name='Scripts SQL MySQL v1.0', halts_service=True)
    rdbms3_meth2.save()
    rdbms3_meth2.method_compatible_with.add(
        ComponentImplementationClass.objects.get(name='int_database_main_mysql_dedicated'))

    # First IS
    is2_1 = Delivery(name='SYSTEM2_INIT', description='Initial delivery')
    is2_1.save()

    is2_1_ii1 = InstallableItem(what_is_installed=rdbms3_v1, belongs_to_set=is2_1, is_full=True, data_loss=True)
    is2_1_ii1.save()
    is2_1_ii1.how_to_install.add(rdbms3_meth1)
    is2_1_ii2 = InstallableItem(what_is_installed=rdbms4_v1, belongs_to_set=is2_1, is_full=True, data_loss=True)
    is2_1_ii2.save()
    is2_1_ii2.how_to_install.add(rdbms3_meth1)

    res.append(is2_1)

    # Second IS
    is2_2 = Delivery(name='SYSTEM2_2', description='Solves all issues. Once again.')
    is2_2.save()

    is2_2_ii1 = InstallableItem(what_is_installed=rdbms3_v2, belongs_to_set=is2_2)
    is2_2_ii1.save()
    is2_2_ii1.how_to_install.add(rdbms3_meth1)
    is2_2_ii2 = InstallableItem(what_is_installed=rdbms4_v2, belongs_to_set=is2_2)
    is2_2_ii2.save()
    is2_2_ii2.how_to_install.add(rdbms3_meth1)

    is2_2_ii1.dependsOn(rdbms3_v1, '==')
    is2_2_ii2.dependsOn(rdbms4_v1, '==')

    res.append(is2_2)

    # Third IS
    is2_3 = Delivery(name='SYSTEM2_3', description='blah.')
    is2_3.save()

    is2_3_ii1 = InstallableItem(what_is_installed=rdbms4_v3, belongs_to_set=is2_3)
    is2_3_ii1.save()
    is2_3_ii1.how_to_install.add(rdbms3_meth1)

    is2_3_ii1.dependsOn(rdbms4_v1, '==')
    is2_3_ii1.dependsOn(rdbms3_v1, '>=')

    res.append(is2_3)

    # Fourth IS
    is2_4 = Delivery(name='SYSTEM2_4', description='blah.')
    is2_4.save()

    is2_4_ii1 = InstallableItem(what_is_installed=rdbms4_v4, belongs_to_set=is2_4)
    is2_4_ii1.save()
    is2_4_ii1.how_to_install.add(rdbms3_meth1)

    is2_4_ii1.dependsOn(rdbms4_v3, '>=')
    is2_4_ii1.dependsOn(rdbms3_v2, '==')

    res.append(is2_4)

    # Fifth IS
    is2_5 = Delivery(name='SYSTEM2_5', description='blah.')
    is2_5.save()

    is2_5_ii1 = InstallableItem(what_is_installed=rdbms4_v5, belongs_to_set=is2_5)
    is2_5_ii1.save()
    is2_5_ii1.how_to_install.add(rdbms3_meth1)

    is2_5_ii1.dependsOn(rdbms4_v1, '>=')
    is2_5_ii1.dependsOn(rdbms4_v3, '<=')

    is2_5_ii1.dependsOn(rdbms3_v2, '==')

    res.append(is2_5)

    # Sixth IS: same version - different deps
    is2_6 = Delivery(name='SYSTEM2_6', description='blah.')
    is2_6.save()

    is2_6_ii1 = InstallableItem(what_is_installed=rdbms4_v5, belongs_to_set=is2_6)
    is2_6_ii1.save()
    is2_6_ii1.how_to_install.add(rdbms3_meth1)

    is2_6_ii1.dependsOn(rdbms4_v4, '==')
    is2_6_ii1.dependsOn(rdbms3_v2, '==')

    res.append(is2_6)

    # Seventh IS: final one - will not be applied, just to keep something to be applied for manual tests
    is2_7 = Delivery(name='SYSTEM2_7', description='blah.')
    is2_7.save()

    is2_7_ii1 = InstallableItem(what_is_installed=rdbms4_v6, belongs_to_set=is2_7)
    is2_7_ii1.save()
    is2_7_ii1.how_to_install.add(rdbms3_meth1)

    is2_7_ii1.dependsOn(rdbms4_v5, '==')
    is2_7_ii1.dependsOn(rdbms3_v2, '==')

    res.append(is2_6)

    # Reverse chain IS 1 (version -1)
    isr2_1 = Delivery(name='SYSTEM2_RV1', description='blah.')
    isr2_1.save()

    isr2_1_ii1 = InstallableItem(what_is_installed=rdbms3_vr1, belongs_to_set=isr2_1)
    isr2_1_ii1.save()
    isr2_1_ii1.how_to_install.add(rdbms3_meth1)

    isr2_1_ii1.dependsOn(rdbms3_v1, '<=')

    res.append(isr2_1)

    # Reverse chain IS 2 (version -2)
    isr2_2 = Delivery(name='SYSTEM2_RV2', description='blah.')
    isr2_2.save()

    isr2_2_ii1 = InstallableItem(what_is_installed=rdbms3_vr2, belongs_to_set=isr2_2)
    isr2_2_ii1.save()
    isr2_2_ii1.how_to_install.add(rdbms3_meth1)

    isr2_2_ii1.dependsOn(rdbms3_vr1, '<=')

    # Reverse chain IS 3 (version -3)
    isr2_3 = Delivery(name='SYSTEM2_RV3', description='blah.')
    isr2_3.save()

    isr2_3_ii1 = InstallableItem(what_is_installed=rdbms3_vr3, belongs_to_set=isr2_3)
    isr2_3_ii1.save()
    isr2_3_ii1.how_to_install.add(rdbms3_meth1)

    isr2_2_ii1.dependsOn(rdbms3_vr2, '>=')


    return res
