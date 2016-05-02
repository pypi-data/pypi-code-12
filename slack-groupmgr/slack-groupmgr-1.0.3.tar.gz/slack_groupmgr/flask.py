"""
Slack slash-command interpreter

Managed semi-secure user groups for Slack.

You can configure this, so that a user that is in one private group can request,
automatically, to be added to other private groups.

    Copyright (c) 2016, Paul Traina
    All rights reserved.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import os
import sys
import io
import json

import appdirs
from flask import Flask, Blueprint, request
from . import SlackGM, ConfigError, UsageError

# Flask standard styles violate PEP8
# pylint: disable=locally-disabled,invalid-name

progname = 'groupmgr'

bp = Blueprint('progname', __name__)

@bp.route("/", methods=['POST'])
def groupmgr():
    """Execute the group manager"""
    authorized_teams = config['slack'].get("authorized_teams", [])
    team_domain = request.form['team_domain']

    if team_domain not in authorized_teams:
        raise ConfigError("slack team {} not recognized".format(team_domain))

    team_config = authorized_teams[team_domain]
    if request.form["token"] not in team_config.get("inbound_tokens", []):
        raise PermissionError("invalid slack integration token for this team")

    opt_admin = request.form['user_name'] in team_config['administrators']
    slackgm = SlackGM(team_config, [request.form['user_name']], admin=opt_admin)

    commands = (request.form['text'] or "help").lower().split()

    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        slackgm.process_command(commands[0], commands[1:])
    except UsageError as err:
        print(str(err) + '\n')
        slackgm.usage()
    sys.stdout.flush()
    response = (sys.stdout.getvalue(), 200, {"Content-Type": "text/plain"})
    sys.stdout.close()
    sys.stdout = original_stdout
    return response


app = Flask(progname)
app.register_blueprint(bp)

dirs = appdirs.AppDirs(progname)
default_config_path = os.path.join(dirs.user_config_dir, 'config.json')
app.config.update(dict(CONFIG_PATH=default_config_path))
app.config.from_envvar("{}_SETTINGS".format(progname.upper()), silent=True)

with open(os.path.expanduser(app.config['CONFIG_PATH']), 'r') as cfg:
    config = json.load(cfg)

def main():
    """Run a standalone debug server (not for production use!)"""
    flask_config = config.get('flask-standalone', {})
    url_prefix = flask_config.get('url-prefix')
    if url_prefix:
        app.register_blueprint(bp, url_prefix=url_prefix)
    ssl_context = flask_config.get('ssl-context')
    if ssl_context:
        ssl_context = tuple(ssl_context)
    app.run(
        host=flask_config.get('bind-host', '0.0.0.0'),
        port=flask_config.get('bind-port', 8443),
        debug=flask_config.get('debug', False),
        ssl_context=ssl_context
    )

if __name__ == '__main__':
    main()
