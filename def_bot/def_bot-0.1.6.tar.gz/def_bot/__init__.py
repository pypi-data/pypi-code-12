from __future__ import unicode_literals
import os
import json
from raven.contrib.flask import Sentry
from flask import Flask
from flask import request
from .def_bot import Def


app = Flask(__name__, instance_relative_config=False)

# App configuration
home_dir = os.path.expanduser('~')
config_path = os.path.join(home_dir, '.config/def/config.py')

if os.path.isfile(config_path):
    app.config.from_pyfile(config_path)

DUNNO_STICKER = app.config.get('DUNNO_STICKER', '')
GO_AWAY_STICKER = app.config.get('GO_AWAY_STICKER', '')
API_TOKEN = app.config.get('API_TOKEN', '')
WEBHOOK = app.config.get('WEBHOOK', '')

# Sentry
try:
    sentry = Sentry(app, dsn=app.config['SENTRY_DSN'])
except KeyError:
    pass


bot = Def(DUNNO_STICKER,
          GO_AWAY_STICKER,
          API_TOKEN,
          WEBHOOK)


@app.route("/"+API_TOKEN, methods=['POST'])
def hook():
    update = json.loads(request.data.decode('utf-8'))
    bot.handle_update(update)
    return 'OK'

