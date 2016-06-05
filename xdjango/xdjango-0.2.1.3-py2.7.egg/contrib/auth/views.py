from django.contrib.auth import get_user_model, login, logout, authenticate
from django.core.mail import send_mail

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from xdjango.rest_framework.mixins import SecureGetObjectMixin
from xdjango.contrib.auth.serializers import UserSerializer, SessionSerializer
from xdjango.contrib.auth.permissions import IsAuthenticatedOrCreateOnly, IsAdminOrOwnOnly
from xdjango.contrib.auth.validators import LoginFormValidator
from xdjango.contrib.auth.responses import INVALID_CREDENTIALS_ERROR_MSG


class UserEmailViewSet(SecureGetObjectMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be created, viewed or edited.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrOwnOnly,)

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_superuser and not self.request.user.is_staff:
            queryset = queryset.filter(pk=self.request.user.pk)
        return queryset

    def create(self, request, *args, **kwargs):
        send_email = self.request.query_params.get('send_email', False)
        email = self.request.data.get('email', None)
        existent_user = None

        try:
            existent_user = self.queryset.get(email=email)
            serializer = self.get_serializer(existent_user)
        except get_user_model().DoesNotExist:
            # This code is based to create method of CreateModelMixin
            # 'https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/mixins.py#L14'
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # prepare data to return
        meta = getattr(serializer, 'Meta', None)
        read_fields = getattr(meta, 'on_creation_read_fields', [])
        data = dict()
        for field in serializer.data:
            if field in read_fields:
                data[field] = serializer.data[field]

        if existent_user:
            existent_user.email_user(subject='Someone wants to register', message='Hello World!')
        elif send_email:
            send_mail(subject='Send invitation',
                      message='Hello World!',
                      from_email='some@123.com',
                      recipient_list=[email])
        else:
            send_mail(subject='New created user without sending invitation',
                      message='Hello!',
                      from_email='some@123.com',
                      recipient_list=['ivanprjcts@gmail.com'])

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class SessionAPIView(APIView):
    """
    Django Session authentication methods.
    """
    permission_classes = (IsAuthenticatedOrCreateOnly,)

    def get(self, request, format=None):
        user = request.user
        context = {"request": request}
        serializer = SessionSerializer(user, context=context)
        return Response(serializer.data)

    def post(self, request, format=None):
        form = LoginFormValidator(request.data)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            if not user:
                return Response(data=INVALID_CREDENTIALS_ERROR_MSG, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if user.is_active:
                    login(request, user)
                    context = {"request": request}
                    serializer = SessionSerializer(user, context=context)
                    return Response(serializer.data)
                else:
                    return Response(data=INVALID_CREDENTIALS_ERROR_MSG, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data=form.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        logout(request)
        return Response()