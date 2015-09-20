from django.test.testcases import TestCase
from ref.models.classifier import AdministrationUnit


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
