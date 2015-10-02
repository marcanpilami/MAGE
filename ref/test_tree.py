from django.contrib.auth.models import Group, User
from django.test.testcases import TestCase
from ref.models.ou import AclAuthorization
from ref.models.classifier import AdministrationUnit, PERMISSIONS


class TestTree(TestCase):
    def setUp(self):
        root = AdministrationUnit.objects.get(name='root')
        b1 = AdministrationUnit(name='B1', description='B1', parent=root)
        b1.save()

        c1 = AdministrationUnit(name='C1', description='C1', parent=b1)
        c1.save()

        c2 = AdministrationUnit(name='C2', description='C2', parent=b1)
        c2.save()

        d1 = AdministrationUnit(name='D1', description='D1', parent=c1)
        d1.save()

        g1 = Group(name='g1')
        g1.save()
        AclAuthorization(target=root, codename='read_folder', group=g1).save()

        a = User.objects.create_superuser('a', 'a@o.fr', 'a')
        a.groups.add(g1)

    def test_scope(self):
        children = AdministrationUnit.objects.get(name="B1").scope()
        children.sort(key=lambda x: x.name)
        self.assertEqual(["B1", "C1", "C2", "D1"], [x.name for x in children])

        children = AdministrationUnit.objects.get(name="root").scope()
        children.sort(key=lambda x: x.name)
        self.assertEqual(["B1", "C1", "C2", "D1", "root"], [x.name for x in children])

        children = AdministrationUnit.objects.get(name="C1").scope()
        children.sort(key=lambda x: x.name)
        self.assertEqual(["C1", "D1"], [x.name for x in children])

    def test_superscope(self):
        parents = AdministrationUnit.objects.get(name="B1").superscope()
        self.assertEqual(["B1", "root"], [x.name for x in parents])

        parents = AdministrationUnit.objects.get(name="D1").superscope()
        self.assertEqual(["D1", "C1", "B1", "root"], [x.name for x in parents])

    def test_acl_bygroup(self):
        acl = AdministrationUnit.objects.get(name="D1").get_acl()

        expected = {}
        for perm in PERMISSIONS:
            expected[perm[0]] = []
        expected['read_folder'] = [Group.objects.get(name='g1').id, ]

        self.assertEqual(expected, acl)

        with self.assertNumQueries(2):
            AdministrationUnit.objects.get(name="D1").get_acl()
            AdministrationUnit.objects.get(name="root").get_acl()

        # Invalidate the root folder => cache should be refreshed
        AclAuthorization(target=AdministrationUnit.objects.get(name="root"), codename='modify_folder',
                         group=Group.objects.get(name='g1')).save()
        with self.assertNumQueries(8):
            AdministrationUnit.objects.get(name="D1").get_acl()

        with self.assertNumQueries(1):
            AdministrationUnit.objects.get(name="B1").get_acl()
