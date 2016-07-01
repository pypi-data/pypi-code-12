from rest_framework import serializers


class PUTSignatureSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    mime_type = serializers.CharField()


class GETSignatureSerializer(serializers.Serializer):
    url = serializers.CharField()
