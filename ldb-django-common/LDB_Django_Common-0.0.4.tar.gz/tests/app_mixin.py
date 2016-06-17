from ldb.django.test.testcases import DjangoAuthAppTestCaseMixin
from django.test.testcases import TransactionTestCase

class ModelTestCase(DjangoAuthAppTestCaseMixin, TransactionTestCase):
    applications = ['test_app', 'ldb.django.contrib.migration']
    root_urlconf = ''

    def test_a(self):
        from test_app.models import TestModel

        a = TestModel(test='asdf', test3='test3')
        a.save()
        a_pk = a.pk
        self.assertEqual(TestModel.objects.get(pk=a_pk).test, 'asdf')
