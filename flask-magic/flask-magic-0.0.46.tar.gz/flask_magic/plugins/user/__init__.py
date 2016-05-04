"""
User Account
"""
import functools
import datetime
from flask import jsonify, make_response
from flask_magic import (Magic, set_meta, get_config, redirect, request, 
                         url_for, session, abort, flash, flash_data, 
                         get_flashed_data, register_package, init_app)
from flask_magic.decorators import (menu, route, template, plugin, login_required,
                              no_login_required, require_user_roles)
from flask_magic.ext import (mail, cache, storage, recaptcha, csrf,
                       user_authenticated, user_not_authenticated)
from flask_magic.exceptions import (ApplicationError, ModelError, UserError)
import flask_magic.utils as utils
from flask_login import (LoginManager, login_user, logout_user, current_user,
                         fresh_login_required, UserMixin)

# Primary Roles
PRIMARY_ROLES = [(99, "SUPERADMIN"),  # ALL MIGHTY, RESERVED FOR SYS ADMIN
                 (98, "ADMIN"),  # App/Site admin
                 (40, "MANAGER"),  # Limited access, but can approve EDITOR Data
                 (30, "EDITOR"),  # Rights to write, manage, publish own data
                 (20, "CONTRIBUTOR"),  # Rights to only write and read own data
                 (10, "USER")  # Simple user
                 ]
# ADMIN
PRIVILEDGED_ROLES = ['superadmin', 'admin', 'manager']

register_package(__package__)

# ------------------------------------------------------------------------------

# The user_model create a fully built model with social signin
def model(db):

    class UserRole(db.Model):

        name = db.Column(db.String(75), index=True)
        level = db.Column(db.Integer, index=True)

        @classmethod
        def new(cls, name, level):
            name = utils.slugify(name)
            role = cls.get_by_name(name)
            if not role:
                role = cls.create(name=name, level=level)
            return role

        @classmethod
        def get_by_name(cls, name):
            name = utils.slugify(name)
            return cls.query().filter(cls.name == name).first()

        @classmethod
        def get_by_level(cls, level):
            return cls.query().filter(cls.level == level).first()

    class User(db.Model, UserMixin):

        role_id = db.Column(db.Integer, db.ForeignKey(UserRole.id))
        email = db.Column(db.String(75), index=True, unique=True)
        email_confirmed = db.Column(db.Boolean, default=False)
        password_hash = db.Column(db.String(255))
        has_temp_login = db.Column(db.Boolean, default=False)
        temp_login_token = db.Column(db.String(100), index=True)
        temp_login_expiration = db.Column(db.DateTime)
        first_name = db.Column(db.String(255))
        last_name = db.Column(db.String(255))
        date_of_birth = db.Column(db.Date)
        sex = db.Column(db.String(10))   # To get confusion out of the way, Sex refers to natural/biological features.
        profile_image_url = db.Column(db.String(255))
        signup_method = db.Column(db.String(255))
        active = db.Column(db.Boolean, default=True, index=True)
        last_login = db.Column(db.DateTime)
        last_visited = db.Column(db.DateTime)
        role = db.relationship(UserRole)

        # ------ FLASK-LOGIN REQUIRED METHODS ----------------------------------

        @property
        def is_active(self):
            return self.active

        # ---------- END FLASK-LOGIN REQUIREMENTS ------------------------------

        @classmethod
        def get_by_email(cls, email):
            """
            Return a User by email address
            """
            return cls.query().filter(cls.email == email).first()

        @classmethod
        def get_by_temp_login(cls, token):
            """
            Return a User by temp_login_token
            temp_login_token allows a user to login with the token
            and reset the password
            """
            user = cls.query().filter(cls.temp_login_token == token).first()
            if user:
                now = datetime.datetime.now()
                if user.has_temp_login is True \
                        and user.temp_login_expiration > now:
                    return user
                user.clear_temp_login()
            return None

        @classmethod
        def get_by_oauth(cls, provider, provider_user_id):
            """
            Get a user by OAuth
            :param provider:
            :param provider_user_id:
            :return: User
            """
            oauth = UserOauthLogin.get_by_provider(provider=provider,
                                                   provider_user_id=provider_user_id)
            return oauth.user if oauth else None
        
        @classmethod
        def new(cls,
                email,
                password=None,
                first_name=None,
                last_name=None,
                role="USER",
                signup_method="email",
                profile_image_url=None,
                **kwargs):
            """
            Create a new user account
            """
            user = cls.get_by_email(email)
            if user:
                raise ModelError("User exists already")
            user = cls.create(email=email,
                              first_name=first_name,
                              last_name=last_name,
                              signup_method=signup_method,
                              profile_image_url=profile_image_url)
            if password:
                user.set_password(password)
            if role:
                role_ = UserRole.get_by_name(role.upper())
                if role_:
                    user.update(role_id=role_.id)

            return user

        @property
        def full_name(self):
            """
            Return the full name
            :return:
            """
            return "%s %s" % (self.first_name, self.last_name)

        @property
        def name(self):
            """
            Alias to first_name
            :return:
            """
            return self.first_name

        def password_matched(self, password):
            """
            Check if the password matched the hash
            :returns bool:
            """
            return utils.verify_encrypted_string(password, self.password_hash)

        def set_password(self, password, random=False):
            """
            Encrypt the password and save it in the DB
            Return the password passed or the new password if randomed
            """
            if random:
                password = utils.generate_random_string()
            self.update(password_hash=utils.encrypt_string(password))
            return password

        def set_temp_login(self, expiration=60):
            """
            Create temp login.
            It will allow to have change password on account
            :param expiration: in minutes the time for expiration
            """
            expiration = datetime.datetime.now() + datetime.timedelta(minutes=expiration)
            while True:
                token = utils.generate_random_string(32).lower()
                if not User.query().filter(User.temp_login_token == token).first():
                    break
            self.update(has_temp_login=True,
                        temp_login_token=token,
                        temp_login_expiration=expiration)
            return token

        def clear_temp_login(self):
            self.update(has_temp_login=False,
                        temp_login_token=None,
                        temp_login_expiration=None)

        def add_oauth(self, provider, provider_user_id, **kwargs):
            """
            To attach a user account to an OAUTH login
            :param provider: the name of the provider
            :param provider_user_id: the id
            :param kwargs:
            :return: Return UserOauthLogin
            """
            u = UserOauthLogin.get_by_provider(provider=provider,
                                               provider_user_id=provider_user_id)
            if u:
                return u
            return UserOauthLogin.create(user_id=self.id,
                                         provider=provider,
                                         provider_user_id=provider_user_id,
                                         **kwargs)

        def has_any_roles(self, *roles):
            """
            Check if user has any of the roles requested
            :param roles: tuple of roles string
            :return: bool
            """
            roles = map(utils.slugify, list(roles))
            for r in UserRole.query().filter(UserRole.name.in_(roles)):
                if r.id == self.role_id:
                    return True
            return False

    class UserOauth(db.Model):
        user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'))
        provider = db.Column(db.String(50), index=True)
        provider_user_id = db.Column(db.String(255))
        name = db.Column(db.String(255))
        email = db.Column(db.String(255))
        profile_image_url = db.Column(db.String(255))
        access_token = db.Column(db.String(255))
        access_key_id = db.Column(db.String(255))
        access_secret_key = db.Column(db.String(255))
        link = db.Column(db.String(255))
        user = db.relationship(User, backref="oauth_logins")

        @classmethod
        def get_by_provider(cls, provider, provider_user_id):
            """
            Returns the entry of the provider and user id
            :params provider: str - the provider name
            :params provider_user_id: 
            """
            return cls.query()\
                .filter(cls.provider == provider)\
                .filter(cls.provider_user_id == provider_user_id)\
                .first()

    return utils.to_struct(User=User,
                           Role=UserRole,
                           OAuth=UserOauth)

# ------------------------------------------------------------------------------

def auth(view, **kwargs):
    """
    This plugin allow user to login to application

    kwargs:
        - signin_view
        - signout_view
        - template_dir
        - menu:
            - title
            - group_name
            - ...

        @plugin(user.login, model=model.User)
        class MyAccount(Magic):
            pass

    """

    endpoint_namespace = view.__name__ + ":%s"
    view_name = view.__name__
    UserModel = kwargs.pop("model")
    User = UserModel.User

    login_view = endpoint_namespace % "login"
    on_signin_view = kwargs.get("signin_view", "Index:index")
    on_signout_view = kwargs.get("signout_view", "Index:index")
    template_dir = kwargs.get("template_dir", "Magic/Plugin/User/Account")
    template_page = template_dir + "/%s.html"

    login_manager = LoginManager()
    login_manager.login_view = login_view
    login_manager.login_message_category = "error"
    init_app(login_manager.init_app)

    menu_context = view
    _menu = kwargs.get("menu", {})
    if _menu:
        @menu(**_menu)
        class UserAccountMenu(object): pass
        menu_context = UserAccountMenu

    @login_manager.user_loader
    def load_user(userid):
        return User.get(userid)

    Magic.g(__USER_AUTH_ENABLED__=True)

    class Auth(object):
        decorators = view.decorators + [login_required]

        SESSION_KEY_SET_EMAIL_DATA = "set_email_tmp_data"
        TEMP_DATA_KEY = "login_tmp_data"

        @property
        def tmp_data(self):
            return session[self.TEMP_DATA_KEY]

        @tmp_data.setter
        def tmp_data(self, data):
            session[self.TEMP_DATA_KEY] = data

        def _login_enabled(self):
            if get_config("USER_AUTH_ALLOW_LOGIN") is not True:
                abort("UserLoginDisabledError")

        def _signup_enabled(self):
            if get_config("USER_AUTH_ALLOW_SIGNUP") is not True:
                abort("UserSignupDisabledError")

        def _oauth_enabled(self):
            if get_config("USER_AUTH_ALLOW_OAUTH") is not True:
                abort("UserOAuthDisabledError")

        def _send_reset_password(self, user):
            delivery = get_config("USER_AUTH_PASSWORD_RESET_METHOD")
            token_reset_ttl = get_config("USER_AUTH_TOKEN_RESET_TTL", 60)
            new_password = None
            if delivery.upper() == "TOKEN":
                token = user.set_temp_login(token_reset_ttl)
                url = url_for(endpoint_namespace % "reset_password",
                              token=token,
                              _external=True)
            else:
                new_password = user.set_password(password=None, random=True)
                url = url_for(endpoint_namespace % "login", _external=True)

            mail.send(template="reset-password.txt",
                         method_=delivery,
                         to=user.email,
                         name=user.email,
                         url=url,
                         new_password=new_password)


        @classmethod
        def login_user(cls, user):
            login_user(user)
            now = datetime.datetime.now()
            user.update(last_login=now, last_visited=now)

        @menu("Login",
              endpoint=endpoint_namespace % "login",
              visible_with_auth_user=False,
              extends=menu_context)
        @template(template_page % "login",
                  endpoint_namespace=endpoint_namespace)
        @route("login/",
               methods=["GET", "POST"],
               endpoint=endpoint_namespace % "login")
        @no_login_required
        def login(self):
            """ Login page """

            self._login_enabled()
            logout_user()
            self.tmp_data = None
            set_meta(title="Login")

            if request.method == "POST":
                email = request.form.get("email").strip()
                password = request.form.get("password").strip()

                if not email or not password:
                    flash("Email or Password is empty", "error")
                    return redirect(url_for(login_view, next=request.form.get("next")))

                user = User.get_by_email(email)
                if user and user.password_hash and user.password_matched(password):
                    self.login_user(user)
                    return redirect(request.form.get("next") or url_for(on_signin_view))
                else:
                    flash("Email or Password is invalid", "error")
                    return redirect(url_for(login_view, next=request.form.get("next")))

            return dict(login_url_next=request.args.get("next", ""),
                        login_url_default=url_for(on_signin_view),
                        signup_enabled=get_config("USER_AUTH_ALLOW_SIGNUP"),
                        oauth_enabled=get_config("USER_AUTH_ALLOW_LOGIN"))

        @menu("Logout",
              endpoint=endpoint_namespace % "logout",
              visible_with_auth_user=True,
              order=100,
              extends=menu_context)
        @route("logout/",
               endpoint=endpoint_namespace % "logout")
        @no_login_required
        def logout(self):
            logout_user()
            return redirect(url_for(on_signout_view or login_view))

        @menu("Signup",
              endpoint=endpoint_namespace % "signup",
              visible_with_auth_user=False,
              extends=menu_context)
        @template(template_page % "signup",
                  endpoint_namespace=endpoint_namespace)
        @route("signup/",
               methods=["GET", "POST"],
               endpoint=endpoint_namespace % "signup")
        @no_login_required
        def signup(self):
            """
            For Email Signup
            :return:
            """
            self._login_enabled()
            self._signup_enabled()
            set_meta(title="Signup")

            if request.method == "POST":
                # reCaptcha
                if not recaptcha.verify():
                    flash("Invalid Security code", "error")
                    return redirect(url_for(endpoint_namespace % "signup",
                                            next=request.form.get("next")))
                try:
                    name = request.form.get("name")
                    email = request.form.get("email")
                    password = request.form.get("password")
                    password2 = request.form.get("password2")
                    profile_image_url = request.form.get("profile_image_url", None)

                    if not name:
                        raise UserError("Name is required")
                    elif not utils.is_email_valid(email):
                        raise UserError("Invalid email address '%s'" % email)
                    elif not password.strip() or password.strip() != password2.strip():
                        raise UserError("Passwords don't match")
                    elif not utils.is_password_valid(password):
                        raise UserError("Invalid password")
                    else:
                        new_account = User.new(email=email,
                                        password=password.strip(),
                                        first_name=name,
                                        profile_image_url=profile_image_url,
                                        signup_method="email")

                        self.login_user(new_account)
                        return redirect(request.form.get("next") or url_for(on_signin_view))
                except ApplicationError as ex:
                    flash(ex.message, "error")
                return redirect(url_for(endpoint_namespace % "signup",
                                        next=request.form.get("next")))

            logout_user()
            return dict(login_url_next=request.args.get("next", ""))

        @route("lost-password/",
               methods=["GET", "POST"],
               endpoint=endpoint_namespace % "lost_password")
        @template(template_page % "lost_password",
                  endpoint_namespace=endpoint_namespace)
        @no_login_required
        def lost_password(self):
            self._login_enabled()
            logout_user()

            set_meta(title="Lost Password")

            if request.method == "POST":
                email = request.form.get("email")
                user = User.get_by_email(email)
                if user:
                    self._send_reset_password(user)
                    flash("A new password has been sent to '%s'" % email, "success")
                else:
                    flash("Invalid email address", "error")
                return redirect(url_for(login_view))
            else:
                return {}


        @menu("Account Settings",
              endpoint=endpoint_namespace % "account_settings",
              order=99,
              visible_with_auth_user=True,
              extends=menu_context)
        @template(template_page % "account_settings",
                  endpoint_namespace=endpoint_namespace)
        @route("account-settings",
               methods=["GET", "POST"],
               endpoint=endpoint_namespace % "account_settings")
        @fresh_login_required
        def account_settings(self):
            set_meta(title="Account Settings")

            if request.method == "POST":
                action = request.form.get("action")
                try:
                    action = action.lower()
                    #
                    if action == "info":
                        first_name = request.form.get("first_name").strip()
                        last_name = request.form.get("last_name", "").strip()

                        data = {
                            "first_name": first_name,
                            "last_name": last_name
                        }
                        current_user.update(**data)
                        flash("Account info updated successfully!", "success")
                    #
                    elif action == "login":
                        confirm_password = request.form.get("confirm-password").strip()
                        if current_user.password_matched(confirm_password):
                            self.change_login_handler()
                            flash("Login Info updated successfully!", "success")
                        else:
                            flash("Invalid password", "error")
                    #
                    elif action == "password":
                        confirm_password = request.form.get("confirm-password").strip()
                        if current_user.password_matched(confirm_password):
                            self.change_password_handler()
                            flash("Password updated successfully!", "success")
                        else:
                            flash("Invalid password", "error")

                    elif action == "profile-photo":
                        file = request.files.get("file")
                        if file:
                            prefix = "profile-photos/%s/" % current_user.id
                            extensions = ["jpg", "jpeg", "png", "gif"]
                            my_photo = storage.upload(file,
                                                      prefix=prefix,
                                                      allowed_extensions=extensions)
                            if my_photo:
                                url = my_photo.url
                                current_user.update(profile_image_url=url)
                                flash("Profile Image updated successfully!", "success")
                    else:
                        raise UserError("Invalid action")

                except Exception as e:
                    flash(e.message, "error")

                return redirect(url_for(endpoint_namespace % "account_settings"))

            return {}

        @classmethod
        def change_login_handler(cls, user_context=None, email=None):
            if not user_context:
                user_context = current_user
            if not email:
                email = request.form.get("email").strip()

            if not utils.is_email_valid(email):
                raise UserWarning("Invalid email address '%s'" % email)
            else:
                if email != user_context.email and User.get_by_email(email):
                    raise UserWarning("Email exists already '%s'" % email)
                elif email != user_context.email:
                    user_context.update(email=email)
                    return True
            return False

        @classmethod
        def change_password_handler(cls, user_context=None, password=None,
                                    password2=None):
            if not user_context:
                user_context = current_user
            if not password:
                password = request.form.get("password").strip()
            if not password2:
                password2 = request.form.get("password2").strip()

            if password:
                if password != password2:
                    raise UserWarning("Password don't match")
                elif not utils.is_password_valid(password):
                    raise UserWarning("Invalid password")
                else:
                    user_context.set_password(password)
                    return True
            else:
                raise UserWarning("Password is empty")


        # OAUTH Login
        @route("oauth-login/<provider>",
               methods=["GET", "POST"],
               endpoint=endpoint_namespace % "oauth_login")
        @template(template_page % "oauth_login",
                  endpoint_namespace=endpoint_namespace)
        @no_login_required
        def oauth_login(self, provider):
            """ Login via oauth providers """

            self._login_enabled()
            self._oauth_enabled()

            provider = provider.lower()
            result = oauth.login(provider)
            response = oauth.response
            popup_js_custom = {
                "action": "",
                "url": ""
            }

            if result:
                if result.error:
                    pass

                elif result.user:
                    result.user.update()

                    oauth_user = result.user
                    user = User.get_by_oauth(provider=provider,
                                             provider_user_id=oauth_user.id)
                    if not user:
                        if oauth_user.email and User.get_by_email(oauth_user.email):
                            flash("Account already exists with this email '%s'. "
                                        "Try to login or retrieve your password " % oauth_user.email, "error")

                            popup_js_custom.update({
                                "action": "redirect",
                                "url": url_for(login_view, next=request.form.get("next"))
                            })

                        else:
                            tmp_data = {
                                "is_oauth": True,
                                "provider": provider,
                                "id": oauth_user.id,
                                "name": oauth_user.name,
                                "picture": oauth_user.picture,
                                "first_name": oauth_user.first_name,
                                "last_name": oauth_user.last_name,
                                "email": oauth_user.email,
                                "link": oauth_user.link
                            }
                            if not oauth_user.email:
                                self.tmp_data = tmp_data

                                popup_js_custom.update({
                                    "action": "redirect",
                                    "url": url_for(endpoint_namespace % "setup_login")
                                })

                            else:
                                try:
                                    picture = oauth_user.picture
                                    user = User.new(email=oauth_user.email,
                                                    name=oauth_user.name,
                                                    signup_method=provider,
                                                    profile_image_url=picture
                                                    )
                                    user.add_oauth(provider,
                                                   oauth_user.provider_id,
                                                   name=oauth_user.name,
                                                   email=oauth_user.email,
                                                   profile_image_url=oauth_user.picture,
                                                   link=oauth_user.link)
                                except ModelError as e:
                                    flash(e.message, "error")
                                    popup_js_custom.update({
                                        "action": "redirect",
                                        "url": url_for(endpoint_namespace % "login")
                                    })
                    if user:
                        self.login_user(user)

                    return dict(popup_js=result.popup_js(custom=popup_js_custom),
                                template_=template_page % "oauth_login")
            return response

        @template(template_page % "setup_login",
                  endpoint_namespace=endpoint_namespace)
        @route("setup-login/", methods=["GET", "POST"], 
               endpoint=endpoint_namespace % "setup_login")
        def setup_login(self):
            """
            Allows to setup a email password if it's not provided specially
            coming from oauth-login
            :return:
            """
            self._login_enabled()
            set_meta(title="Setup  Login")

            # Only user without email can set email
            if current_user.is_authenticated() and current_user.email:
                return redirect(url_for(endpoint_namespace % "account_settings"))

            if self.tmp_data:
                if request.method == "POST":
                    if not self.tmp_data["is_oauth"]:
                        return redirect(endpoint_namespace % "login")

                    try:
                        email = request.form.get("email")
                        password = request.form.get("password")
                        password2 = request.form.get("password2")

                        if not utils.is_email_valid(email):
                            raise UserError("Invalid email address '%s'" % email)
                        elif User.get_by_email(email):
                            raise UserError("An account exists already with this email address '%s' " % email)
                        elif not password.strip() or password.strip() != password2.strip():
                            raise UserError("Passwords don't match")
                        elif not utils.is_password_valid(password):
                            raise UserError("Invalid password")
                        else:
                            user = User.new(email=email,
                                            password=password.strip(),
                                            name=self.tmp_data["name"],
                                            profile_image_url=self.tmp_data["picture"],
                                            signup_method=self.tmp_data["provider"])

                            user.add_oauth(self.tmp_data["provider"],
                                           self.tmp_data["id"],
                                           name=self.tmp_data["name"],
                                           email=email,
                                           profile_image_url=self.tmp_data["picture"],
                                           link=self.tmp_data["link"])

                            self.login_user(user)
                            self.tmp_data = None

                        return redirect(request.form.get("next") or url_for(on_signin_view))
                    except ApplicationError as ex:
                        flash(ex.message, "error")
                        return redirect(url_for(endpoint_namespace % "login"))

                return dict(provider=self.tmp_data)

            else:
                return redirect(url_for(endpoint_namespace % "login"))

        @route("reset-password/<token>",
               methods=["GET", "POST"],
               endpoint=endpoint_namespace % "reset_password")
        @template(template_page % "reset_password",
                  endpoint_namespace=endpoint_namespace)
        @no_login_required
        def reset_password(self, token):
            self._login_enabled()
            logout_user()

            set_meta(title="Reset Password")
            user = User.get_by_temp_login(token)
            if user:
                if not user.has_temp_login:
                    return redirect(url_for(on_signin_view))
                if request.method == "POST":
                    try:
                        self.change_password_handler(user_context=user)
                        user.clear_temp_login()
                        flash("Password updated successfully!", "success")
                        return redirect(url_for(on_signin_view))
                    except Exception as ex:
                        flash("Error: %s" % ex.message, "error")
                        return redirect(url_for(endpoint_namespace % "reset_password",
                                                token=token))
                else:
                    return dict(token=token)
            else:
                abort(404, "Invalid token")

        @route("oauth-connect", methods=["POST"], 
               endpoint="%s:oauth_connect" % endpoint_namespace)
        def oauth_connect(self):
            """ To login via social """
            email = request.form.get("email").strip()
            name = request.form.get("name").strip()
            provider = request.form.get("provider").strip()
            provider_user_id = request.form.get("provider_user_id").strip()
            image_url = request.form.get("image_url").strip()
            next = request.form.get("next", "")
            try:
                current_user.oauth_connect(provider=provider,
                                         provider_user_id=provider_user_id,
                                         email=email,
                                         name=name,
                                         image_url=image_url)
            except Exception as ex:
                flash("Unable to link your account", "error")

            return redirect(url_for(endpoint_namespace % "account_settings"))

    return Auth

# ------------------------------------------------------------------------------

def admin(view, **kwargs):
    
    route_base = "user-admin"

    UserModel = kwargs.get("model")
    User = UserModel.User
    Role = UserModel.Role

    template_dir = kwargs.get("template_dir", "Magic/Plugin/User/Admin")
    template_page = template_dir + "/%s.html"

    _menu = kwargs.get("menu", {})
    _menu.setdefault("title", "Users")
    _menu.setdefault("group_name", "admin")
    _menu["visible_with_auth_user"] = True

    # Create a Admin menu for query the methods in Admin
    @menu(**_menu)
    class UserAdminMenu(object): pass

    def admin_deco(func):
        """
        Decorator to check on user's roles when logged in
        :param func:
        :return:
        """
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            if current_user and current_user.is_authenticated:
                return require_user_roles(*PRIVILEDGED_ROLES)(func)(*args, **kwargs)
            return func(*args, **kwargs)
        return decorator

    @plugin(auth, model=UserModel, menu={
        "title": "My Account",
        "align_right": True,
        "group_name": _menu.get("group_name"),
        "show_profile_avatar": True,
        "show_profile_name": True}
    )
    class Admin(object):
        decorators = view.decorators + [login_required, admin_deco]

        @classmethod
        def _validate_admin_roles(cls, user):
            admin = current_user

        @classmethod
        def _user_roles_options(cls):
            _r = Role.query()\
                .filter(Role.level <= current_user.role.level)\
                .order_by(Role.level.desc())
            return [(r.id, r.name) for r in _r]

        @menu("All Users", endpoint="UserAdmin:index", order=1, extends=UserAdminMenu)
        @template(template_page % "index")
        @route("%s/" % route_base, endpoint="UserAdmin:index")
        def user_admin_index(self):

            set_meta(title="Users - User Admin")
            per_page = get_config("APPLICATION_PAGINATION_PER_PAGE", 25)

            page = request.args.get("page", 1)
            include_deleted = True if request.args.get("include-deleted") == "y" else False
            name = request.args.get("name")
            email = request.args.get("email")
            role = request.args.get("role")
            sorting = request.args.get("sorting", "first_name__asc")

            users = User.query(include_deleted=include_deleted)
            users = users.join(Role).filter(Role.level <= current_user.role.level)

            if name:
                users = users.filter(User.first_name.contains(name))
            if email:
                users = users.filter(User.email.contains(email))
            if role:
                users = users.filter(User.role_id == int(role))
            if sorting and "__" in sorting:
                col, dir = sorting.split("__", 2)
                if dir == "asc":
                    users = users.order_by(getattr(User, col).asc())
                else:
                    users = users.order_by(getattr(User, col).desc())

            users = users.paginate(page=page, per_page=per_page)

            sorting = [("first_name__asc", "Name ASC"),
                       ("first_name__desc", "Name DESC"),
                       ("email__asc", "Email ASC"),
                       ("email__desc", "Email DESC"),
                       ("created_at__asc", "Signup ASC"),
                       ("created_at__desc", "Signup Desc"),
                       ("last_login__asc", "Login ASC"),
                       ("last_login__desc", "Login Desc")]
            return dict(user_roles_options=self._user_roles_options(),
                        sorting_options=sorting,
                        users=users,
                        search_query={
                            "include-deleted": request.args.get("include-deleted", "n"),
                            "role": int(request.args.get("role")) if request.args.get("role") else "",
                            "status": request.args.get("status"),
                            "first_name": request.args.get("name", ""),
                            "email": request.args.get("email", ""),
                            "sorting": request.args.get("sorting")})

        @menu("User Roles", endpoint="UserAdmin:roles", order=2, extends=UserAdminMenu)
        @template(template_page % "roles")
        @route("%s/roles" % route_base, methods=["GET", "POST"], endpoint="UserAdmin:roles")
        @require_user_roles("superadmin", "admin")
        def user_admin_roles(self):
            """
            Only admin and super admin can add/remove roles
            RESTRICTED ROLES CAN'T BE CHANGED
            """
            roles_max_range = 11
            if request.method == "POST":
                try:
                    id = request.form.get("id")
                    name = request.form.get("name")
                    level = request.form.get("level")
                    action = request.form.get("action")

                    if name and level:
                        level = int(level)
                        name = name.upper()
                        _levels = [r[0] for r in PRIMARY_ROLES]
                        _names = [r[1] for r in PRIMARY_ROLES]
                        if level in _levels or name in _names:
                            raise UserError("Can't modify PRIMARY Roles - name: %s, level: %s " % (name, level))
                        else:
                            if id:
                                role = Role.get(id)
                                if role:
                                    if action == "delete":
                                        role.delete()
                                        flash("Role '%s' deleted successfully!" % role.name, "success")
                                    elif action == "update":
                                        if role.level != level and Role.get_by_level(level):
                                            raise UserError("Role Level '%s' exists already" % level)
                                        elif role.name != name and Role.get_by_name(name):
                                            raise UserError("Role Name '%s'  exists already" % name)
                                        else:
                                            role.update(name=name, level=level)
                                            flash("Role '%s (%s)' updated successfully" % (name, level), "success")
                                else:
                                    raise UserError("Role doesn't exist")
                            else:
                                if Role.get_by_level(level):
                                    raise UserError("Role Level '%s' exists already" % level)
                                elif Role.get_by_name(name):
                                    raise UserError("Role Name '%s'  exists already" % name)
                                else:
                                    Role.new(name=name, level=level)
                                    flash("New Role '%s (%s)' addedd successfully" % (name, level), "success")
                except ApplicationError as ex:
                    flash("Error: %s" % ex.message, "error")
                return redirect(url_for("UserAdmin:roles"))
            else:
                set_meta(title="User Roles - Users Admin")
                roles = Role.query().order_by(Role.level.desc())

                allocated_levels = [r.level for r in roles]
                levels_options = [(l, l) for l in range(1, roles_max_range) if l not in allocated_levels]

                return dict(roles=roles,
                            levels_options=levels_options)

        @menu("Info", endpoint="UserAdmin:get", visible=False, extends=UserAdminMenu)
        @template(template_page % "get")
        @route("%s/<id>" % route_base, endpoint="UserAdmin:get")
        def user_admin_get(self, id):
            set_meta(title="User Info - Users Admin")
            user = User.get(id, include_deleted=True)
            if not user:
                abort(404, "User doesn't exist")

            if current_user.role.level < user.role.level:
                abort(403, "Not enough rights to access this user info")

            return dict(user=user, 
                        user_roles_options=self._user_roles_options())

        @route("%s/post" % route_base, methods=["POST"], endpoint="UserAdmin:post")
        def user_admin_post(self):
            try:
                id = request.form.get("id")
                user = User.get(id, include_deleted=True)
                if not user:
                    flash("Can't change user info. Invalid user", "error")
                    return redirect(url_for("UserAdmin:index"))

                if current_user.role.level < user.role.level:
                    abort(403, "Not enough rights to update this user info")

                email = request.form.get("email", "").strip()
                first_name = request.form.get("first_name", "")
                last_name = request.form.get("last_name", "")
                user_role = request.form.get("user_role")
                action = request.form.get("action")

                if user.id != current_user.id:
                    _role = Role.get(user_role)
                    if not _role:
                        raise UserError("Invalid role")

                    if current_user.role.name.lower() not in PRIVILEDGED_ROLES:
                        raise UserError("Not Enough right to change user's info")

                    if action == "activate":
                        user.update(active=True)
                        flash("User has been ACTIVATED", "success")
                    elif action == "deactivate":
                        user.update(active=False)
                        flash("User is now DEACTIVATED", "success")
                    elif action == "delete":
                        user.delete()
                        flash("User has been deleted", "success")
                    elif action == "undelete":
                        user.delete(False)
                        flash("User is now active", "success")
                    else:
                        if email and email != user.email:
                            if not utils.is_email_valid(email):
                                raise UserError("Invalid email address '%s'" % email)
                            else:
                                if User.get_by_email(email):
                                    raise UserError("Email exists already '%s'" % email)
                                user.update(email=email)

                        user.update(first_name=first_name,
                                    last_name=last_name,
                                    role_id=_role.id)

                else:
                    if email and email != user.email:
                        if not utils.is_email_valid(email):
                            raise UserError("Invalid email address '%s'" % email)
                        else:
                            if User.get_by_email(email):
                                raise UserError("Email exists already '%s'" % email)
                            user.update(email=email)
                    user.update(first_name=first_name,
                                last_name=last_name)

                    flash("User's Info updated successfully!", "success")
            except ApplicationError as ex:
                flash("Error: %s " % ex.message, "error")
            return redirect(url_for("UserAdmin:get", id=id))

        @route("%s/reset-password" % route_base, methods=["POST"], endpoint="UserAdmin:reset_password")
        def user_admin_reset_password(self):
            """
            Reset the password
            :returns string: The new password string
            """
            try:
                id = request.form.get("id")
                user = User.get(id)
                if not user:
                    raise UserError("Invalid User")

                self._send_reset_password(user)
                flash("Password Reset instruction is sent to email", "success")
            except ApplicationError as ex:
                flash("Error: %s " % ex.message, "error")
            return redirect(url_for("UserAdmin:get", id=id))

        @route("%s/create" % route_base, methods=["POST"], endpoint="UserAdmin:create")
        @require_user_roles(*PRIVILEDGED_ROLES)
        def user_admin_create(self):
            try:
                email = request.form.get("email")
                first_name = request.form.get("first_name", "")
                last_name = request.form.get("last_name", "")
                user_role = request.form.get("user_role")

                _role = Role.get(user_role)
                if not _role:
                    raise UserError("Invalid role")

                if current_user.role.level < _role.level:
                    raise UserError("Can't be assigned a greater user role")

                if not first_name:
                    raise UserError("First Name is required")
                elif not email:
                    raise UserError("Email is required")
                elif not utils.is_email_valid(email):
                    raise UserError("Invalid email address")
                if User.get_by_email(email):
                    raise UserError("Email '%s' exists already" % email)
                else:
                    user = User.new(email=email,
                                    first_name=first_name,
                                    last_name=last_name,
                                    signup_method="email-from-admin",
                                    role_id=_role.id)
                    if user:
                        flash("User created successfully!", "success")
                        return redirect(url_for("UserAdmin:get", id=user.id))
                    else:
                        raise UserError("Couldn't create new user")
            except ApplicationError as ex:
                flash("Error: %s" % ex.message, "error")
            return redirect(url_for("UserAdmin:index"))

    return Admin


# ------------------------------------------------------------------------------
def setup(model, admin_email, password=None):

    # :: USERS
    # Setup primary roles.
    # PRIMARY ROLES is a set of tuples [(level, name), ...]
    [model.Role.new(level=r[0], name=r[1]) for r in PRIMARY_ROLES]

    user = model.User.get_by_email(admin_email)
    if not user:
        model.User.new(email=admin_email,
                       password=password,
                       first_name="Admin",
                       last_name="Super",
                       role="superadmin")
        return True

