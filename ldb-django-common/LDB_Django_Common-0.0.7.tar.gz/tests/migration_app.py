from ldb.django.test.testcases import DjangoAuthAppTestCaseMixin
from django.test.testcases import TransactionTestCase


class ModelTestCase(DjangoAuthAppTestCaseMixin, TransactionTestCase):
    applications = ['test_app', 'ldb.django.contrib.migration']
    root_urlconf = ''

    def getTestModel(self, state):
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection

        executor = MigrationExecutor(connection)
        old_state = [('test_app', state)]
        old_apps = executor.loader.project_state(old_state).apps
        executor.migrate(old_state)
        TestModel = old_apps.get_model('test_app', 'TestModel')

        return TestModel

    def setUp(self):
        TestModel = self.getTestModel('0002_testmodel_test2')
        TestModel.objects.create(test='test', test2='test2')
        a = TestModel(test='test_2', test2='test2_2')
        a.save()

    def test_a(self):
        from test_app.models import TestModel
        self.getTestModel('0003_move_model_add_test3')

        self.assertEqual(TestModel.objects.get(test='test').test, 'test')

        a = TestModel(test='hello', test3='asdf')
        a.save()

    def test_b(self):
        from test_app.models import TestModel
        self.getTestModel('0003_move_model_update')

        self.assertEqual(TestModel.objects.get(test='test').test, 'test')
        self.assertEqual(TestModel.objects.get(test='test').test3, 'test2')
        self.assertEqual(TestModel.objects.get(test='test').test3, 'test2')

        a = TestModel(test='hello', test3='asdf')
        a.save()

    def test_c(self):
        from test_app.models import TestModel
        self.getTestModel('0003_move_model_remove_test2')

        self.assertEqual(TestModel.objects.get(test='test').test, 'test')
        self.assertEqual(TestModel.objects.get(test='test').test3, 'test2')
        self.assertEqual(TestModel.objects.get(test='test').test3, 'test2')

        a = TestModel(test='hello', test3='asdf')
        a.save()
