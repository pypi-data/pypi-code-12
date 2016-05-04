import requests

from django.contrib.auth import login
from django.views.generic import RedirectView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from . import exceptions

UserModel = get_user_model()


class CallbackView(RedirectView):
    acquire_access_token_url = 'https://auth.sch.bme.hu/oauth2/token'
    auth_sch_profile_url = 'https://auth.sch.bme.hu/api/profile/'
    success_url = None
    error_url = None
    internal_id_field_name = None
    refresh_token_field_name = None

    def get(self, request, *args, **kwargs):
        try:
            code = request.GET.get('code')
            state = request.GET.get('state')
            self.verify_state(state)
            api_tokens = self.get_api_tokens(code)
            profile = self.get_profile(api_tokens['access_token'])
            self.url = self.success_url
            self.get_or_create_user(profile['internal_id'])
            self.save_refresh_token(self.user, api_tokens['refresh_token'])
            self.login_user(self.user)
            self.authentication_successful(profile, self.user)
        except Exception as exception:
            self.url = self.error_url
            self.authentication_failed(exception)

        return super(CallbackView, self).get(request, *args, **kwargs)

    def get_or_create_user(self, internal_id):
        """Létrehozza a felhasználót, ha még nem létezik, és beállítja a self.user-be."""
        self.user, created = UserModel.objects.get_or_create(
            **{self.get_internal_id_field_name(): internal_id}
        )
        return self.user, created

    def save_refresh_token(self, user, refresh_token):
        """Elmenti a refresh_token-t, ha szükséges.
        :param user: A felhasználó.
        :param refresh_token: A refresh_token.
        """
        refresh_token_field_name = self.get_refresh_token_field_name()
        if refresh_token_field_name:
            setattr(user, refresh_token_field_name, refresh_token)
            user.save()

    def get_api_tokens(self, code):
        """Megszerzi az access és a refresh tokeneket.
        :param code: A token lekéréséhez használandó kód.
        :return: A lekérdezésre a válasz deszerializálva. Tartalmazza az access és a refresh tokent.
        """
        try:
            data = {
                'grant_type': 'authorization_code',
                'code': code
            }
            response = requests.post(
                self.acquire_access_token_url,
                data=data,
                auth=(settings.AUTH_SCH['CLIENT_ID'], settings.AUTH_SCH['SECRET_KEY'])
            )

            return response.json()
        except KeyError:
            raise ImproperlyConfigured(
                "You must define AUTH_SCH['CLIENT_ID'], and AUTH_SCH['SECRET_KEY']. Check the documentation."
            )

    def get_profile(self, access_token):
        """Az felhasználó profilját kéri le az auth.sch-ból.
        :param access_token: A felhasználó adataihoz hozzáférést nyújtó token.
        :return: A felhasználó profilja dictionary-ként.
        """
        data = {
            'access_token': access_token
        }

        r = requests.get(
            self.auth_sch_profile_url,
            params=data
        )
        return r.json()

    def get_internal_id_field_name(self):
        """Visszaadja az internal_id mező nevét.
        :return: Az internal_id mező neve.
        """
        if self.internal_id_field_name:
            return self.internal_id_field_name
        elif settings.AUTH_SCH.get('INTERNAL_ID_FIELD_NAME'):
            return settings.AUTH_SCH.get('INTERNAL_ID_FIELD_NAME')
        else:
            return 'auth_sch_internal_id'

    def get_refresh_token_field_name(self):
        """Visszaadja a refresh token tárolására használt mező nevét a user modellben.
        :return: A refresh token tárolására használt mező neve. Ha None, akkor nem kell elmenteni a refresh tokent.
        """
        if self.refresh_token_field_name:
            return self.refresh_token_field_name
        elif settings.AUTH_SCH.get('REFRESH_TOKEN_FIELD_NAME'):
            return settings.AUTH_SCH.get('REFRESH_TOKEN_FIELD_NAME')
        else:
            return None

    def authentication_successful(self, profile, user):
        """Ezt hívjuk meg akkor, amikor az autentikáció sikeres volt. Ez azt jelenti, hogy kaptunk hozzáférést
        (access token-t), és sikeresen le tudtuk kérdezni a felhasználó profilját."""
        pass

    def authentication_failed(self, exception):
        """Ezt akkor hívjuk meg, ha az autentikáció sikertelen volt."""
        pass

    def login_user(self, user):
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        return login(self.request, user)

    def verify_state(self, state):
        if state != self.request.session['authsch_state']:
            raise exceptions.VerificationException(
                'The returned state is not the same as the state stored in the session.'
            )
