from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'pk', 'last_login', 'is_superuser', 'email', 'is_staff', 'is_active', 'date_joined')
        read_only_fields = ('last_login', 'is_superuser', 'date_joined', 'pk')
        on_creation_read_fields = ('url', 'email', 'pk')


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'pk', 'last_login', 'email', 'is_staff', 'is_superuser')