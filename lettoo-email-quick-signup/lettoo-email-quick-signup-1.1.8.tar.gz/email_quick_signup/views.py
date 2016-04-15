from django.http import HttpRequest
from django.views.generic.edit import FormView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token

from . import app_settings
from .forms import SignupForm, PasswordResetForm, SetPasswordForm, ChangeEmailForm
from .utils import get_form_class, complete_signup, send_email_confirmation
from .models import QuickEmailConfirmation, QuickEmailAddress
from .status import ApiStatus, KEY_FIELD_REQUIRED, CONFIRMATION_DOES_NOT_EXIST, VERIFICATION_KEY_INVALID, \
    VERIFICATION_KEY_VERIFIED, EMAIL_FIELD_REQUIRED, EMAIL_ADDRESS_DOES_NOT_EXIST, REFUSED_TO_RESEND_EMAIL, \
    REQUEST_METHOD_NOT_ALLOWED, USER_DOES_NOT_EXIST, CHANGE_EMAIL_ADDRESS_EXIST


class RegisterView(APIView, FormView):
    """
    Accepts the credentials and creates a new user
    if user does not exist already
    Return the REST Token if the credentials are valid and authenticated.
    Calls allauth complete_signup method

    Accept the following POST parameters: username, email, password
    Return the REST Framework Token Object's key.
    """

    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')
    token_model = Token
    form_class = SignupForm

    def get(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def form_valid(self, form):
        self.user = form.save(self.request)
        self.token, created = self.token_model.objects.get_or_create(user=self.user)
        if isinstance(self.request, HttpRequest):
            request = self.request
        else:
            request = self.request._request
        return complete_signup(request, self.user)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(RegisterView, self).get_form_kwargs(*args, **kwargs)
        kwargs['data'] = self.request.data
        return kwargs

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, 'email_quick_signup', self.form_class)

    def post(self, request, *args, **kwargs):
        self.initial = {}
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        if self.form.is_valid():
            self.form_valid(self.form)
            result = self.user.dict()
            result['key'] = self.token.key
            return Response(result, status=status.HTTP_200_OK)
        else:
            return self.get_response_with_errors()

    def get_response_with_errors(self):
        return Response(self.form.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')
    token_model = Token

    def get(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        self.kwargs['email'] = self.request.data.get('email', '')
        self.kwargs['key'] = self.request.data.get('key', '')

        if not self.kwargs['email']:
            return Response(ApiStatus(EMAIL_FIELD_REQUIRED).get_json(), status=status.HTTP_400_BAD_REQUEST)

        if not self.kwargs['key']:
            return Response(ApiStatus(KEY_FIELD_REQUIRED).get_json(), status=status.HTTP_400_BAD_REQUEST)

        confirmation = self.get_object()

        if not confirmation:
            return Response(ApiStatus(CONFIRMATION_DOES_NOT_EXIST).get_json(), status=status.HTTP_400_BAD_REQUEST)

        email_address, result = confirmation.confirm(self.request)

        if result == 'invalid':
            if app_settings.INVALID_AUTO_RESEND_CONFIRMATION:
                send_email_confirmation(request, email_address=email_address, signup=True)
            return Response(ApiStatus(VERIFICATION_KEY_INVALID).get_json(), status=status.HTTP_400_BAD_REQUEST)
        elif result == 'verified':
            return Response(ApiStatus(VERIFICATION_KEY_VERIFIED).get_json(), status=status.HTTP_400_BAD_REQUEST)
        else:
            token, created = self.token_model.objects.get_or_create(user=email_address.user)
            result = email_address.user.dict()
            result['key'] = token.key
            return Response(result, status=status.HTTP_200_OK)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(key=self.kwargs["key"].lower())
        except QuickEmailConfirmation.DoesNotExist:
            return None

    def get_queryset(self):
        qs = QuickEmailConfirmation.objects.filter(email_address__email=self.kwargs["email"])
        qs = qs.select_related("email_address__user")
        return qs


class ResendEmailView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')
    token_model = Token

    def get(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        self.kwargs['email'] = self.request.data.get('email', '')

        if not self.kwargs['email']:
            return Response(ApiStatus(EMAIL_FIELD_REQUIRED).get_json(), status=status.HTTP_400_BAD_REQUEST)

        email_address = self.get_object()

        if not email_address:
            return Response(ApiStatus(EMAIL_ADDRESS_DOES_NOT_EXIST).get_json(), status=status.HTTP_400_BAD_REQUEST)

        send_email = send_email_confirmation(request, email_address.user, signup=True)

        if send_email:
            token, created = self.token_model.objects.get_or_create(user=email_address.user)
            result = email_address.user.dict()
            result['key'] = token.key
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(ApiStatus(REFUSED_TO_RESEND_EMAIL).get_json(), status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        if queryset and len(queryset) > 0:
            return queryset[0]
        else:
            return None

    def get_queryset(self):
        qs = QuickEmailAddress.objects.filter(email=self.kwargs["email"])
        return qs


class PasswordResetView(APIView, FormView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')
    form_class = PasswordResetForm
    token_model = Token

    def get(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, 'email_quick_password_reset', self.form_class)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(PasswordResetView, self).get_form_kwargs(*args, **kwargs)
        kwargs['data'] = self.request.data
        return kwargs

    def post(self, request, *args, **kwargs):
        self.initial = {}
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        if self.form.is_valid():
            user = self.form.save()

            if user:
                if send_email_confirmation(request, user, signup=False, check_verified=False):
                    token, created = self.token_model.objects.get_or_create(user=user)
                    result = user.dict()
                    result['key'] = token.key
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    return Response(ApiStatus(REFUSED_TO_RESEND_EMAIL).get_json(), status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(ApiStatus(USER_DOES_NOT_EXIST).get_json(), status=status.HTTP_400_BAD_REQUEST)
        else:
            return self.get_response_with_errors()

    def get_response_with_errors(self):
        return Response(self.form.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView, FormView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')
    form_class = SetPasswordForm
    token_model = Token

    def get(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, 'email_quick_password_reset_confirm', self.form_class)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(PasswordResetConfirmView, self).get_form_kwargs(*args, **kwargs)
        kwargs['data'] = self.request.data
        return kwargs

    def post(self, request, *args, **kwargs):
        self.initial = {}
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        if self.form.is_valid():
            confirmation, password = self.form.save()

            if not confirmation:
                return Response(ApiStatus(CONFIRMATION_DOES_NOT_EXIST).get_json(), status=status.HTTP_400_BAD_REQUEST)

            email_address, result = confirmation.confirm(self.request, check_verified=False)

            if result == 'invalid':
                if app_settings.INVALID_AUTO_RESEND_CONFIRMATION:
                    send_email_confirmation(self.request, email_address.user, signup=False, check_verified=False)
                return Response(ApiStatus(VERIFICATION_KEY_INVALID).get_json(), status=status.HTTP_400_BAD_REQUEST)
            else:
                email_address.user.set_password(password)
                email_address.user.save()
                token, created = self.token_model.objects.get_or_create(user=email_address.user)
                result = email_address.user.dict()
                result['key'] = token.key
                return Response(result, status=status.HTTP_200_OK)
        else:
            return self.get_response_with_errors()

    def get_response_with_errors(self):
        return Response(self.form.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(APIView, FormView):
    permission_classes = (IsAuthenticated,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')
    form_class = ChangeEmailForm
    token_model = Token

    def get(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        return Response(ApiStatus(REQUEST_METHOD_NOT_ALLOWED).get_json(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, 'email_quick_change', self.form_class)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(ChangeEmailView, self).get_form_kwargs(*args, **kwargs)
        kwargs['data'] = self.request.data
        return kwargs

    def post(self, request, *args, **kwargs):
        self.initial = {}
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        if self.form.is_valid():
            email = self.form.cleaned_data['email']

            if QuickEmailAddress.objects.filter(email=email, user=request.user, verified=True).exists():
                return Response(ApiStatus(CHANGE_EMAIL_ADDRESS_EXIST).get_json(), status=status.HTTP_400_BAD_REQUEST)

            if QuickEmailAddress.objects.filter(email=email).exclude(user=request.user).exists():
                return Response(ApiStatus(CHANGE_EMAIL_ADDRESS_EXIST).get_json(), status=status.HTTP_400_BAD_REQUEST)

            email_address, created = QuickEmailAddress.objects.get_or_create(user=request.user, email=email)
            # email_address.change(request, email, confirm=False)
            send_email = send_email_confirmation(request, email_address=email_address, signup=False)

            if send_email:
                token, created = self.token_model.objects.get_or_create(user=email_address.user)
                result = email_address.user.dict()
                result['key'] = token.key
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(ApiStatus(REFUSED_TO_RESEND_EMAIL).get_json(), status=status.HTTP_400_BAD_REQUEST)
        else:
            return self.get_response_with_errors()

    def get_response_with_errors(self):
        return Response(self.form.errors, status=status.HTTP_400_BAD_REQUEST)