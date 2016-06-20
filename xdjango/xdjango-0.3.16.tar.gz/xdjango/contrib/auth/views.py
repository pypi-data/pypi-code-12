import socket

from django.conf import settings
from django.core.mail import send_mail
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

from xdjango.contrib.auth.serializers import UserSerializer, SessionSerializer, read_safe_fields
from xdjango.contrib.auth.permissions import IsAuthenticatedOrCreateOnly, IsAdminOrOwnOnly, is_valid_one_time_token
from xdjango.contrib.auth.validators import (
    LoginFormValidator, UserQueryValidator, PasswordResetFormValidator, EmailFormValidator
)
from xdjango.contrib.auth.responses import INVALID_CREDENTIALS_ERROR_MSG
from xdjango.contrib.auth.tokens import default_token_generator
from xdjango.shortcuts import get_object_or_none


def send_reset_password_email(request, user, subject):
    token = default_token_generator.make_token(user=user)
    user_id = user.pk

    server_address = request.build_absolute_uri('/')
    reset_url = server_address + "preset/%s/%s" % (user_id, token)

    data = {
        'url_reset_password': reset_url,
    }

    template = get_template('xdjango/email_new_account.html')
    html_message = template.render(Context(data))

    try:
        user.email_user(subject=subject, message="", html_message=html_message)
        return
    except socket.gaierror as exc:
        return [_("Email couldn't be sent.")]


class UserEmailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be created, viewed or edited.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrOwnOnly,)

    def get_object_or_none(self, queryset):
        """
        Returns the object the view is displaying.
        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        if lookup_url_kwarg not in self.kwargs:
            return None

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_none(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_superuser:
            return queryset
        elif self.request.user.is_staff:
            return queryset.filter(is_superuser=False)
        else:
            instance = self.get_object_or_none(queryset)
            if instance is not None:
                user = instance
            else:
                user = self.request.user
            return queryset.filter(pk=user.pk)

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
        data = read_safe_fields(serializer)

        if existent_user and send_email:
            # transparent behaviour
            errors = send_reset_password_email(request, user, _('Send invitation'))
        elif send_email:
            errors = send_reset_password_email(request, user, _('Send invitation'))
        else:
            errors = None

        if errors is not None:
            data["errors"] = errors
            return Response(data, status=status.HTTP_202_ACCEPTED, headers=headers)

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


class OneTimeTokenAPIView(APIView):
    """
    Django One-Time Token authentication method.
    """
    permission_classes = ()

    def post(self, request, format=None):
        form = EmailFormValidator(request.data)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = get_user_model().objects.get(email=email)
                errors = send_reset_password_email(request, user, _("Reset password"))
                if errors is not None:
                    return Response(errors, status=status.HTTP_202_ACCEPTED)

            except get_user_model().DoesNotExist:
                recipient = getattr(settings, 'EMAIL_TO_NULL', 'dev.null.recipient@gmail.com')
                send_mail(subject="log - reset password",
                          message="Someone tried to reset password from a non-existent account",
                          from_email="some@123.com",
                          recipient_list=[recipient])

            return Response(data="", status=status.HTTP_201_CREATED)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


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


class RequestResetPasswordView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'xdjango/request_reset_password.html', context)
