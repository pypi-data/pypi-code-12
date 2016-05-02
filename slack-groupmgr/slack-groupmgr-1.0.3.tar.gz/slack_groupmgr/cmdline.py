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
import json
import argparse

import appdirs

from . import SlackGM, ConfigError, UsageError

def main():
    """ Workhorse """
    dirs = appdirs.AppDirs('groupmgr')
    default_config_path = os.path.join(dirs.user_config_dir, 'config.json')

    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config-path', default=default_config_path,
                        help='configuration info (default: {})'.format(default_config_path))
    parser.add_argument('-t', '--team', dest='team', help='slack team')
    parser.add_argument('-u', '--users', dest='users',
                        default=[], action='append', help='slack usernames')
    parser.add_argument('command', nargs='?', help='command')
    parser.add_argument('arguments', nargs='*', help='arguments')
    args = parser.parse_args()

    with open(os.path.expanduser(args.config_path), 'r') as cfg:
        config = json.load(cfg)

    team_domain = args.team or config['default-team']
    authorized_teams = config['slack'].get("authorized_teams", [])
    if team_domain not in authorized_teams:
        raise ConfigError("slack team {} not recognized".format(team_domain))

    slackgm = SlackGM(authorized_teams[team_domain], args.users, admin=True)
    try:
        slackgm.process_command(args.command, args.arguments)
    except UsageError as err:
        print(str(err) + '\n')
        slackgm.usage()


if __name__ == "__main__":
    main()
