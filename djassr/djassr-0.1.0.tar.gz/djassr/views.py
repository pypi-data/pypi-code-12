from rest_framework import generics
from rest_framework.response import Response

import s3sign

from . import serializers


DEFAULT_VALID = 60  # seconds


class BaseGetSignature(generics.GenericAPIView):
    def post(self, request):
        args = self._get_args(request)
        valid = self.get_valid(request)
        signer = self.signer()
        data = signer.get_signed_url(*args, valid)
        return Response(data)

    def get_valid(self, request):
        return DEFAULT_VALID


class BaseGetPUTSigneature(BaseGetSignature):
    serializer_class = serializers.PUTSignatureSerializer

    def _get_args(self, request):
        file_name = request.POST.get('file_name')
        mime_type = request.POST.get('mime_type')
        return file_name, mime_type


class GetPUTSignature(BaseGetPUTSigneature):
    signer = s3sign.S3PUTSigner


class GetPUTPublicSignature(BaseGetPUTSigneature):
    signer = s3sign.S3PUTPublicSigner


class GetGETSignature(BaseGetSignature):

    serializer_class = serializers.GETSignatureSerializer

    signer = s3sign.S3GETSigner

    def _get_args(self, request):
        return (request.POST.get('url'), )
