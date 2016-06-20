from django.contrib.auth import get_user_model

from rest_framework import serializers


def read_safe_fields(serializer):
    meta = getattr(serializer, 'Meta', None)
    read_fields = getattr(meta, 'safe_fields', [])
    data = dict()
    for field in serializer.data:
        if field in read_fields:
            data[field] = serializer.data[field]
    return data


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'pk', 'last_login', 'is_superuser', 'email', 'is_staff', 'is_active', 'date_joined', 'password')
        read_only_fields = ('last_login', 'is_superuser', 'date_joined', 'pk')
        write_only_fields = ('password',)
        safe_fields = ('url', 'email', 'pk')

    def update(self, instance, validated_data):
        instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.email = validated_data.get('email', instance.email)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        password = validated_data.get('password', None)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'pk', 'last_login', 'email', 'is_staff', 'is_superuser')