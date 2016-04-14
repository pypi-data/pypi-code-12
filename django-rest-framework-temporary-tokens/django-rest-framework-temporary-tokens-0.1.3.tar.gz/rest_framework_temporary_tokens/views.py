"""Utility views for Temporary Tokens.
Classes:
    ObtainTemporaryAuthToken: View to provide tokens to clients.
    
( Inspired by 
https://github.com/JamesRitchie/django-rest-framework-expiring-tokens,
https://github.com/JamesRitchie/django-rest-framework-expiring-tokens/blob/master/LICENSE )
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.conf import settings

from models import TemporaryToken


class ObtainTemporaryAuthToken(ObtainAuthToken):
    """Enables username/password exchange for expiring token."""
    model = TemporaryToken

    def post(self, request):
        """Respond to POSTed username/password with token."""
        serializer = AuthTokenSerializer(data=request.data)

        if( serializer.is_valid() 
            or (    'USE_AUTHENTICATION_BACKENDS' 
                    in settings.REST_FRAMEWORK_TEMPORARY_TOKENS  
                    and settings.REST_FRAMEWORK_TEMPORARY_TOKENS['USE_AUTHENTICATION_BACKENDS']) ):
            user = None
            try:
                user = serializer.validated_data['user']
            except KeyError:
                if( 'email' in request.data
                    and 'username' in request.data
                    and 'password' in request.data ):
                    user = authenticate(    email=request.data['email'],
                                            username=request.data['username'],
                                            password=request.data['password'] )
                elif(   'email' in request.data
                        and 'password' in request.data ):
                    user = authenticate(    email=request.data['email'],
                                            password=request.data['password'] ) 

            token = None           
            if user:
                token, _created = TemporaryToken.objects.get_or_create(user=user)

            if token and token.expired:
                # If the token is expired, generate a new one.
                token.delete()
                token = TemporaryToken.objects.create(
                    user=user
                )

            if token:
                data = {'token': token.key}
                return Response(data)
            else:
                error =  _('Could not authenticate user')
                return Response(    {'error': error}, 
                                    status=HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

obtain_temporary_auth_token = ObtainTemporaryAuthToken.as_view()

