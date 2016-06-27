from django.contrib.auth import get_user_model
from django_autoshard.tests.base import TestBase

User = get_user_model()


class UserTests(TestBase):
    def test__create__user__success(self):
        u1 = User.objects.create(
            username='test',
            email='test@local.dev'
        )
        u2 = User.objects.get(email='test@local.dev')
        self.assertEqual(u1, u2)
