from django.contrib.auth import get_user_model, login, logout, authenticate
from django.template.loader import get_template
from django.template import Context
from django.views.generic import View
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from xdjango.contrib.auth.serializers import UserSerializer, SessionSerializer
from xdjango.contrib.auth.permissions import IsAuthenticatedOrCreateOnly, IsAdminOrOwnOnly
from xdjango.contrib.auth.validators import LoginFormValidator, UserQueryValidator, PasswordResetFormValidator
from xdjango.contrib.auth.responses import INVALID_CREDENTIALS_ERROR_MSG
from xdjango.contrib.auth.tokens import default_token_generator


class UserEmailViewSet(viewsets.ModelViewSet):
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

    @staticmethod
    def _on_creation_read_data(serializer):
        meta = getattr(serializer, 'Meta', None)
        read_fields = getattr(meta, 'on_creation_read_fields', [])
        data = dict()
        for field in serializer.data:
            if field in read_fields:
                data[field] = serializer.data[field]
        return data

    @staticmethod
    def _send_reset_password_email(request, user, subject):
        token = default_token_generator.make_token(user=user)
        user_id = user.pk

        server_address = request.build_absolute_uri('/')
        reset_url = server_address + "preset/%s/%s" % (user_id, token)

        data = {
            'url_reset_password': reset_url,
        }

        template = get_template('xdjango/email_new_account.html')
        html_message = template.render(Context(data))

        user.email_user(subject=subject, message="", html_message=html_message)

    def create(self, request, *args, **kwargs):
        field_label = "email"
        query_params = UserQueryValidator(request.query_params)
        if query_params.is_valid():
            send_email = query_params.cleaned_data['send_email']
        else:
            send_email = False

        # This code is based to create method of CreateModelMixin
        # 'https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/mixins.py#L14'
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            message = _("%(model_name)s with this %(field_label)s already exists.") % \
                      {"model_name": self.serializer_class.Meta.model.__name__, "field_label": _("email address")}
            if field_label not in serializer.errors or message not in serializer.errors[field_label]:
                raise
            # email already exists, so get email from data
            existent_user = True
            email = request.data.get(field_label)
            user = self.queryset.get(email=email)
            serializer = self.get_serializer(user)
        else:
            existent_user = False
            self.perform_create(serializer)
            email = serializer.data.get(field_label)
            user = self.queryset.get(email=email)

        headers = self.get_success_headers(serializer.data)
        data = self._on_creation_read_data(serializer)

        if existent_user and send_email:
            # transparent behaviour
            self._send_reset_password_email(request, user, 'Send invitation')
        elif send_email:
            self._send_reset_password_email(request, user, 'Send invitation')
        else:
            pass  # do nothing

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


class ResetView(View):
    def get(self, request, *args, **kwargs):
        token = kwargs.get("token", None)
        user_id = kwargs.get("user_id", None)

        if token == "0":
            token = None

        context = {
            'token': token,
            'user_id': user_id,
        }
        return render(request, 'xdjango/reset_password.html', context)

    def post(self, request, *args, **kwargs):
        form = PasswordResetFormValidator(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            token = form.cleaned_data['token']
            user_id = form.cleaned_data['user_id']
            email = form.clean_email()

            if user_id:
                user = get_user_model().objects.get(pk=user_id)
            elif email:
                user = get_user_model().objects.get(email=email)
            else:
                return redirect("/")

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()

        return redirect("/")