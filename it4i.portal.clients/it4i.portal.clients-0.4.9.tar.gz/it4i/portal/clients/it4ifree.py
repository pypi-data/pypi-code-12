#!/usr/bin/env python
"""
Show some basic information from IT4I PBS accounting
"""
import getopt
import getpass
import re
import simplejson as json
import sys
import xmlrpclib

from logger import LOGGER
from lxml import etree
from tabulate import tabulate

table_me_title = 'Projects I am participating in'
table_me_as_pi_title = 'Projects I am Primarily Investigating'


def errmsg(msg, retval=1):
    """
    print help and exit
    """

    if not msg:
        my_name = __name__.split('.')[-1]
        LOGGER.error('usage: %s', my_name)
        LOGGER.error('       %s -h|--help', my_name)
        LOGGER.error('''
The command shows some basic information from IT4I PBS accounting. The
data is related to the current user and to all projects in which he/she
participates.

After the invocation, the user is asked for his/her IT4I login/password.

Columns of "%s":
         PID: Project ID/account string.
   Days left: Days till the given project expires.
       Total: Corehours allocated to the given project.
        Used: Sum of core hours used by all project members.
    ...by me: Corehours used by the current user only.
        Free: Corehours that haven't yet been utilized.

Columns of "%s" (if present):
         PID: Project ID/account string.
       Login: Project member's login name.
        Used: Project member's used core hours.

''', table_me_title, table_me_as_pi_title)
    else:
        LOGGER.error(msg)
    sys.exit(retval)


def yes_no(prompt='Do you really want to continue (yes/no)?: '):
    while True:
        try:
            input = raw_input(prompt)
        except KeyboardInterrupt:
            print >> sys.stdout
            continue
        if input.lower() in ('yes', 'ye', 'y'):
            return True
        elif input.lower() in ('no', 'n'):
            return False


def main(argv=sys.argv[1:]):
    """
    main function
    """

    # parse opts and args
    try:
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.GetoptError as err:
        LOGGER.error(str(err))
        errmsg(None)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            errmsg(None)

    from config import config_files
    from config import config
    from config import api_url

    if not api_url.startswith('https://'):
        LOGGER.error("The API URL is not secured using https://")
        if not yes_no():
            sys.exit(1)

    try:
        username_optname = "it4i_username"
        username = config.get("main", username_optname)
    except:
        LOGGER.error('''No IT4I username specified in your config file, try setting:
%s = <your_username_here>

Suggested paths:
%s
''', username_optname, config_files)
        sys.stdout.write('Username: ')
        username = sys.stdin.readline()

    username = username.strip()
    password = getpass.getpass()
    remote = re.sub('://', '://%s:%s@' % (username, password), api_url, 1)
    try:
        server = xmlrpclib.ServerProxy(remote, verbose=False)
    except:
        errmsg('Sorry, there was a problem accessing the service. Please try again later.')

    try:
        xmlout = getattr(server, 'xmlrpc_it4ifree')()
    except:
        errmsg('Wrong password?')

    root = etree.XML(xmlout)
    jsonout = json.loads(root.find(".//params/param/value/string").text)

    table_me = []
    for row in jsonout['me']:
        table_me.append([row['pid'],
                         row['days_left'],
                         row['total'],
                         row['used'],
                         row['used_by_me'],
                         row['free']])
    table_me_headers = ['PID',
                        'Days left',
                        'Total',
                        'Used',
                        '...by me',
                        'Free']

    table_me_as_pi = []
    row_previous = ''
    for row in jsonout['me_as_pi']:
        table_me_as_pi.append([row['pid'] if row['pid'] != row_previous else '',
                               row['login'],
                               row['core_hours']])
        row_previous = row['pid']
    table_me_as_pi_headers = ['PID',
                              'Login',
                              'Used']

    if table_me:
        print >> sys.stdout, '\n%s\n%s' % (table_me_title,
                                           len(table_me_title) * '=')
        print tabulate(table_me, table_me_headers)

    if table_me_as_pi:
        print >> sys.stdout, '\n%s\n%s' % (table_me_as_pi_title,
                                           len(table_me_as_pi_title) * '=')
        print tabulate(table_me_as_pi, table_me_as_pi_headers)


if __name__ == "__main__":
    main()
