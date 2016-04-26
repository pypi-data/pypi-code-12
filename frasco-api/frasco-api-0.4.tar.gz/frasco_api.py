from frasco import Feature, Service, action, hook, abort, current_app, request, jsonify, g, Blueprint
from frasco_models import as_transaction, transaction, save_model
import datetime
import base64
import hashlib
import uuid
import re
from apispec import APISpec
from flask_cors import CORS


class ApiService(Service):
    @hook('before_request')
    def set_api_flag(self):
        g.is_api_call = True


class AuthenticatedApiService(ApiService):
    @hook('before_request')
    def authenticate_before_request(self):
        if request.method != 'OPTIONS' and not current_app.features.users.logged_in():
            return jsonify({"error": "Request an API key from your account"}), 403


_url_arg_re = re.compile(r"<([a-z]:)?([a-z0-9_]+)>")
def convert_url_args(url):
    return _url_arg_re.sub(r"{\2}", url)


def convert_type_to_spec(type):
    if type is int:
        return "integer"
    if type is float:
        return "number"
    if type is bool:
        return "boolean"
    return "string"


class ApiFeature(Feature):
    name = 'api'
    requires = ['models', 'users']
    defaults = {"default_key_duration": None,
                "allow_cross_requests": True,
                "cors_options": {},
                "cors_resources": {},
                "cors_allow_services": True,
                "spec_title": "API",
                "spec_version": "1.0"}

    def init_app(self, app):
        if self.options['allow_cross_requests']:
            resources = dict(**self.options['cors_resources'])
            if self.options['cors_allow_services']:
                resources[app.config['SERVICES_URL_PREFIX'] + '/*'] = {"origins": "*"}
            cors = CORS(app, resources=resources, **self.options['cors_options'])

        self.app = app
        self.model = app.features.models.ensure_model('ApiKey',
            user=app.features.users.model,
            value=dict(type=str, index=True),
            last_accessed_at=datetime.datetime,
            last_accessed_from=str,
            expires_at=datetime.datetime)

        @app.features.users.login_manager.header_loader
        def load_user_from_header(header_val):
            header_val = header_val.replace('Basic ', '', 1)
            try:
                header_val = base64.b64decode(header_val)
                key_value = header_val.split(':')[0]
            except Exception:
                return
            key = app.features.models.find_first('ApiKey', value=key_value, not_found_404=False)
            if key:
                with transaction():
                    now = datetime.datetime.utcnow()
                    if key.expires_at and key.expires_at < now:
                        return None
                    key.last_accessed_at = now
                    key.last_accessed_from = request.remote_addr
                    save_model(key)
                return key.user

        spec_bp = Blueprint("apispec", __name__)
        @spec_bp.route("/spec.json")
        def get_spec():
            return jsonify(**self.build_spec().to_dict())
        app.register_service_blueprint(spec_bp)

    @action('create_api_key', default_option='user', as_='api_key')
    @as_transaction
    def create_key(self, user=None, expires_at=None):
        if not expires_at and self.options['default_key_duration']:
            expires_at = datetime.datetime.now() + datetime.timedelta(
                seconds=self.options['default_key_duration'])
        key = self.model()
        key.value = hashlib.sha1(str(uuid.uuid4)).hexdigest()
        key.user = user or current_app.features.users.current
        key.expires_at = expires_at
        save_model(key)
        return key

    def build_spec(self):
        spec = APISpec(title=self.options['spec_title'],
                       version=self.options['spec_version'],
                       basePath=self.app.config['SERVICES_URL_PREFIX'])
        for name, srv in self.app.services.iteritems():
            paths = {}
            tag = {"name": name}
            if srv.__doc__:
                tag["description"] = srv.__doc__
            spec.add_tag(tag)
            for view in srv.views:
                params = []
                if hasattr(view.func, 'request_params'):
                    for p in reversed(view.func.request_params):
                        for pname in p.names:
                            o = {"name": pname,
                                 "type": convert_type_to_spec(p.type),
                                 "required": p.required}
                            if p.help:
                                o['description'] = p.help
                            params.append(o)
                path = paths.setdefault(convert_url_args(view.url_rules[-1][0]), {})
                for method in view.url_rules[-1][1].get('methods', ['GET']):
                    o = {"operationId": view.name,
                         "parameters": params,
                         "tags": [name]}
                    if view.func.__doc__:
                        o['description'] = view.func.__doc__
                    path[method.lower()] = o

            for path, operations in paths.iteritems():
                spec.add_path(path=path, operations=operations)

        return spec