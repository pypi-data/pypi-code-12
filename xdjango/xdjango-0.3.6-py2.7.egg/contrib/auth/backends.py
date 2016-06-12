from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class AntiBruteForceModelBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL preventing brute-force attacks.
    UserModel must have 'failed_login_attempts' field
    """
    MAX_FAIL_LOGIN_ATTEMPTS = 50

    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
            if not (user.failed_login_attempts < self.MAX_FAIL_LOGIN_ATTEMPTS):
                # Reset password
                user.set_password(None)
                user.initialize_failed_attempts_counter()
                # saved
                return
            elif user.check_password(password):
                user.initialize_failed_attempts_counter()
                return user
            else:
                user.increment_failed_attempts_counter()
        except UserModel.DoesNotExist:
            pass
        # Run the default password hasher once to reduce the timing
        # difference between an existing and a non-existing user (#20760).
        UserModel().set_password(password)
