from django import test

from ievv_opensource.ievv_customsql import customsql_registry


class TestRegistry(test.TestCase):
    def test_add(self):
        class MockCustomSql(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('myapp', MockCustomSql)
        self.assertIn(MockCustomSql, mockregistry._customsql_classes)
        self.assertIn('myapp', mockregistry._customsql_classes_by_appname_map)
        self.assertIn(MockCustomSql, mockregistry._customsql_classes_by_appname_map['myapp'])

    def test_add_multiple_to_same_appname(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('myapp', MockCustomSql1)
        mockregistry.add('myapp', MockCustomSql2)
        self.assertIn(MockCustomSql1, mockregistry._customsql_classes)
        self.assertIn(MockCustomSql2, mockregistry._customsql_classes)
        self.assertIn('myapp', mockregistry._customsql_classes_by_appname_map)
        self.assertIn(MockCustomSql1, mockregistry._customsql_classes_by_appname_map['myapp'])
        self.assertIn(MockCustomSql2, mockregistry._customsql_classes_by_appname_map['myapp'])

    def test_remove(self):
        class MockCustomSql(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('myapp', MockCustomSql)

        mockregistry.remove('myapp', MockCustomSql)
        self.assertNotIn(MockCustomSql, mockregistry._customsql_classes)
        self.assertNotIn('myapp', mockregistry._customsql_classes_by_appname_map)

    def test_contains(self):
        class MockCustomSql(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        self.assertFalse(MockCustomSql in mockregistry)
        mockregistry.add('myapp', MockCustomSql)
        self.assertTrue(MockCustomSql in mockregistry)

    def test_remove_one_of_multiple_in_same_app(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('myapp', MockCustomSql1)
        mockregistry.add('myapp', MockCustomSql2)

        mockregistry.remove('myapp', MockCustomSql2)
        self.assertNotIn(MockCustomSql2, mockregistry._customsql_classes)
        self.assertNotIn(MockCustomSql2, mockregistry._customsql_classes_by_appname_map['myapp'])
        self.assertIn(MockCustomSql1, mockregistry._customsql_classes)
        self.assertIn('myapp', mockregistry._customsql_classes_by_appname_map)

    def test_iter(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql3(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('my_first_app', MockCustomSql1)
        mockregistry.add('my_first_app', MockCustomSql2)
        mockregistry.add('my_second_app', MockCustomSql3)

        iter_list = list(mockregistry)
        self.assertTrue(isinstance(iter_list[0], MockCustomSql1))
        self.assertTrue(isinstance(iter_list[1], MockCustomSql2))
        self.assertTrue(isinstance(iter_list[2], MockCustomSql3))

    def test_iter_appnames(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql3(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('my_first_app', MockCustomSql1)
        mockregistry.add('my_first_app', MockCustomSql2)
        mockregistry.add('my_second_app', MockCustomSql3)

        self.assertEqual(['my_first_app', 'my_second_app'],
                         list(mockregistry.iter_appnames()))

    def test_iter_customsql_in_appname(self):
        class MockCustomSql1(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql2(customsql_registry.AbstractCustomSql):
            pass

        class MockCustomSql3(customsql_registry.AbstractCustomSql):
            pass

        mockregistry = customsql_registry.MockableRegistry()
        mockregistry.add('my_first_app', MockCustomSql1)
        mockregistry.add('my_first_app', MockCustomSql2)
        mockregistry.add('my_second_app', MockCustomSql3)

        iter_list = list(mockregistry.iter_customsql_in_appname('my_first_app'))
        self.assertEqual(2, len(iter_list))
        self.assertTrue(isinstance(iter_list[0], MockCustomSql1))
        self.assertTrue(isinstance(iter_list[1], MockCustomSql2))
