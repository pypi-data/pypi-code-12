from django.contrib.auth.models import User, Group
from rest_framework import exceptions
from rest_framework import serializers

from . models import UserSecret


class UserSerializer(serializers.ModelSerializer):

	secret = serializers.SerializerMethodField('get_secret_key')
	
	class Meta:
		model = User
		fields =  ('id', 'username', 'password', 'email', 'first_name', 'last_name','secret',)
		write_only_fields = ('password',)
		read_only_fields = ('id',)
		
	def create(self, validated_data):
		user = User.objects.create(
			username=validated_data['username'],
			email=validated_data['email'],
			first_name=validated_data['first_name'],
			last_name=validated_data['last_name']
			)

		user.set_password(validated_data['password'])
		user.save()
		
		return user

	def get_secret_key(self, obj):
		
		try:
			user_secret = UserSecret.objects.get(user=obj)
			return user_secret.key
		except UserSecret.DoesNotExist:
			print "does not exist"
			return ""


class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = ('__all__')

