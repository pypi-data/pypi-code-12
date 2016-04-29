import os
import flask.ext.restless
import flask.ext.bcrypt
import flask.ext.httpauth
import flask.ext.security
from flask.ext.security.utils import encrypt_password, verify_password
import flask_jwt

from bookbank import BBCONF_PATH_LIBBASE

from .app import app
from .database import db

flask_bcrypt = flask.ext.bcrypt.Bcrypt(app)

from .models import *

security = flask.ext.security.Security(app, user_datastore)

# flask-httpauth
# auth = flask.ext.httpauth.HTTPBasicAuth()

# JWT Token authentication  ===================================================
def authenticate(username, password):
    user = user_datastore.find_user(email=username)
    if user and username == user.email and verify_password(password, user.password):
        return user
    return None


def load_user(payload):
    user = user_datastore.find_user(id=payload['identity'])
    return user


jwt = flask_jwt.JWT(app, authenticate, load_user)

# Flask-Restless API  =========================================================
@flask_jwt.jwt_required()
def auth_func(**kw):
    pass


# init api
api_manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
api_manager.create_api(SomeStuff,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/api/v1',
    collection_name='free_stuff',
    include_columns=['id', 'data1', 'data2', 'user_id'])
api_manager.create_api(SomeStuff,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/api/v1',
    preprocessors=dict(GET_SINGLE=[auth_func], GET_MANY=[auth_func]),
    collection_name='protected_stuff',
    include_columns=['id', 'data1', 'data2', 'user_id'])

def create_test_models():
    user_datastore.create_user(email='test', password=encrypt_password('test'))
    user_datastore.create_user(email='test2', password=encrypt_password('test2'))
    stuff = SomeStuff(data1=2, data2='toto', user_id=1)
    db.session.add(stuff)
    stuff = SomeStuff(data1=5, data2='titi', user_id=1)
    db.session.add(stuff)
    db.session.commit()


@app.before_first_request
def bootstrap_app():
    debug_string = ""
    for k in app.config:
        debug_string += "%s: %s\n" % (k, app.config[k])
    app.logger.info(debug_string)
    if not app.config['TESTING']:
        if db.session.query(User).count() == 0:
            create_test_models()

