from django.test import TestCase

from django.contrib.auth.models import User
from  .models import UserSecret


class UserRegistrationTestCase(TestCase):
	def setUp(self):
		print ">>>creating an instance of User"
		User.objects.create(username='test_username', password='test_password', email='me@iamkel.com', first_name='kel', last_name='testme',)

	def test_user_is_exists(self):
		test_user = User.objects.get(username="test_username")
		self.assertEqual(test_user.password, 'test_password')


	def test_user_has_secret(self):
		test_user = User.objects.get(username="test_username")
		self.assertTrue(test_user.secret.key)
		print ">>>secret:%s" % test_user.secret.key

		self.assertTrue(test_user.secret.key)
		print ">>>verified:%s" % test_user.secret.is_verified
