__author__ = 'schlitzer'
# stdlib
import argparse
import configparser
import os
import signal
import sys
import time
import logging
from logging.handlers import TimedRotatingFileHandler

# 3rd party
from bottle import run
import jsonschema
import jsonschema.exceptions
from pep3143daemon import DaemonContext, PidFile
import pymongo
from requestlogger import WSGILogger, ApacheFormatter
from wsgi_request_id import RequestID

# Project
from el_aap_api.app import app, app_logger
from el_aap_api.controllers import *
from el_aap_api.models import *
from el_aap_api.errors import error_catcher
from el_aap_api.schemas import *


def main():
    parser = argparse.ArgumentParser(description="ElasticSearch Authentication and Authorization Proxy API")

    parser.add_argument("--cfg", dest="cfg", action="store",
                        default="/etc/el_aap/el_aap_api.ini",
                        help="Full path to configuration")

    parser.add_argument("--pid", dest="pid", action="store",
                        default="/var/run/el_aap/el_aap_api.pid",
                        help="Full path to PID file")

    parser.add_argument("--nodaemon", dest="nodaemon", action="store_true",
                        help="Do not daemonize, run in foreground")

    subparsers = parser.add_subparsers(help='commands', dest='method')
    subparsers.required = True

    quit_parser = subparsers.add_parser('quit', help='Stop ElasticSearch Authentication and Authorization Proxy API')
    quit_parser.set_defaults(method='quit')

    start_parser = subparsers.add_parser('start', help='Start ElasticSearch Authentication and Authorization Proxy API')
    start_parser.set_defaults(method='start')

    devel_parser = subparsers.add_parser('devel', help='Start ElasticSearch Authentication and Authorization Proxy API in developement mode')
    devel_parser.set_defaults(method='devel')

    indicies_parser = subparsers.add_parser('indices', help='create indices and exit')
    indicies_parser.set_defaults(method='indices')

    admin_parser = subparsers.add_parser('create_admin', help='create default admin user')
    admin_parser.set_defaults(method='create_admin')

    parsed_args = parser.parse_args()

    if parsed_args.method == 'quit':
        el_aapapi = ElasticSearchAAPAPI(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aapapi.quit()

    elif parsed_args.method == 'start':
        el_aapapi = ElasticSearchAAPAPI(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aapapi.start()

    elif parsed_args.method == 'devel':
        el_aapapi = ElasticSearchAAPAPI(
                cfg=parsed_args.cfg,
                pid=parsed_args.pid,
                nodaemon=parsed_args.nodaemon
        )
        el_aapapi.start(devel=True)

    elif parsed_args.method == 'indices':
        el_aapapi = ElasticSearchAAPAPI(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aapapi.manage_indices()

    elif parsed_args.method == 'create_admin':
        el_aapapi = ElasticSearchAAPAPI(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aapapi.create_admin()


class ElasticSearchAAPAPI(object):
    def __init__(self, cfg, pid, nodaemon):
        self._config_file = cfg
        self._config = configparser.ConfigParser()
        self._config_dict = None
        self._mongo_pools = dict()
        self._mongo_colls = dict()
        self._pid = pid
        self._nodaemon = nodaemon
        self.log = logging.getLogger('el_aap')

    def _acc_logging(self):
        acc_handlers = []
        access_log = self.config.get('file:logging', 'acc_log')
        access_retention = self.config.getint('file:logging', 'acc_retention')
        acc_handlers.append(TimedRotatingFileHandler(access_log, 'd', access_retention))
        return acc_handlers

    def _app_logging(self):
        logfmt = logging.Formatter('%(asctime)sUTC - %(levelname)s - %(message)s')
        logfmt.converter = time.gmtime
        app_handlers = []
        aap_level = self.config.get('file:logging', 'app_loglevel')
        app_log = self.config.get('file:logging', 'app_log')
        app_retention = self.config.getint('file:logging', 'app_retention')
        app_handlers.append(TimedRotatingFileHandler(app_log, 'd', app_retention))

        for handler in app_handlers:
            handler.setFormatter(logfmt)
            self.log.addHandler(handler)
        self.log.setLevel(aap_level)
        self.log.debug("application logger is up")

    def _pw_recovery(self):
        try:
            if 'pw_recovery' in self._config_dict:
                jsonschema.validate(self.config_dict['pw_recovery'], CHECK_CONFIG_PW_RECOVERY)
            else:
                return
        except jsonschema.exceptions.ValidationError as err:
            print("pw_recovery section: {0}".format(err))
            sys.exit(1)
        try:
            tmpl = self.config.get('pw_recovery', 'text_tmpl')
            with open(tmpl) as f:
                self.config_dict['pw_recovery']['text_tmpl'] = f.read()
        except FileNotFoundError:
            print("could not read text_tmpl: {0}".format(tmpl))
            sys.exit(1)
        try:
            tmpl = self.config.get('pw_recovery', 'html_tmpl')
            with open(tmpl) as f:
                self.config_dict['pw_recovery']['html_tmpl'] = f.read()
        except FileNotFoundError:
            print("could not read html_tmpl: {0}".format(tmpl))
            sys.exit(1)

    def _app(self, devel=False):
        self._app_logging()
        self.log.info("starting up")
        self._pw_recovery()
        self._setup_pools()
        self._setup_colls()

        m_lostpw = LostPW(self._mongo_colls['lostpw'])
        m_permissions = Permissions(self._mongo_colls['permissions'])
        m_roles = Roles(self._mongo_colls['roles'])
        m_sessions = Sessions(self._mongo_colls['sessions'])
        m_users = Users(self._mongo_colls['users'])
        m_aa = AuthenticationAuthorization(m_users, m_sessions)

        app.install(MetaPlugin(m_lostpw, 'm_lostpw'))
        app.install(MetaPlugin(m_permissions, 'm_permissions'))
        app.install(MetaPlugin(m_roles, 'm_roles'))
        app.install(MetaPlugin(m_sessions, 'm_sessions'))
        app.install(MetaPlugin(m_users, 'm_users'))
        app.install(MetaPlugin(m_aa, 'm_aa'))
        app.install(MetaPlugin(self.config_dict, 'm_config'))
        app.install(error_catcher)

        logapp = RequestID(WSGILogger(app, self._acc_logging(), ApacheFormatter()))

        self.log.info("startup done, now serving")
        run(app=logapp, host='0.0.0.0', port=self.config.getint('main', 'port'), debug=devel, reloader=devel, server='waitress')

    @staticmethod
    def _cfg_to_dict(config):
        result = {}
        for section in config.sections():
            result[section] = {}
            for option in config.options(section):
                try:
                    result[section][option] = config.getint(section, option)
                    continue
                except ValueError:
                    pass
                try:
                    result[section][option] = config.getfloat(section, option)
                    continue
                except ValueError:
                    pass
                try:
                    result[section][option] = config.getboolean(section, option)
                    continue
                except ValueError:
                    pass
                try:
                    result[section][option] = config.get(section, option)
                    continue
                except ValueError:
                    pass
        return result

    def _setup_pools(self):
        self.log.info("setting up mongodb connection pools")
        for section in self.config.sections():
            if section.endswith(':mongopool'):
                try:
                    jsonschema.validate(self.config_dict[section], CHECK_CONFIG_MONGOPOOL)
                except jsonschema.exceptions.ValidationError as err:
                    print("{0} section: {1}".format(section, err))
                    sys.exit(1)
                sectionname = section.rsplit(':', 1)[0]
                self.log.debug("setting up mongodb connection pool {0}".format(sectionname))
                pool = pymongo.MongoClient(
                    host=self.config.get(section, 'hosts'),
                    serverSelectionTimeoutMS=10
                )
                db = pool.get_database(self.config.get(section, 'db'))
                try:
                    user = self.config.get(section, 'user')
                    password = self.config.get(section, 'pass')
                    db.authenticate(user, password)
                    self.log.debug("connection pool {0} is using authentication".format(sectionname))
                except configparser.NoOptionError:
                    self.log.debug("connection pool {0} is not using authentication".format(sectionname))
                self._mongo_pools[sectionname] = db
                self.log.debug("setting up mongodb connection pool {0} done".format(sectionname))
        self.log.info("setting up mongodb connection pools done")

    def _setup_colls(self):
        self.log.info("setting up mongodb collections")
        for section in self.config.sections():
            if section.endswith(':mongocoll'):
                try:
                    jsonschema.validate(self.config_dict[section], CHECK_CONFIG_MONGOCOLL)
                except jsonschema.exceptions.ValidationError as err:
                    print("{0} section: {1}".format(section, err))
                    sys.exit(1)
                sectionname = section.rsplit(':', 1)[0]
                self.log.debug("setting up mongodb collection {0}".format(sectionname))
                pool_name = self.config.get(section, 'pool')
                coll_name = self.config.get(section, 'coll')
                self.log.debug("mongodb collection {0} is using mongodb connection pool {1}".format(sectionname, pool_name))
                self.log.debug("mongodb collection {0} is using collection name {1}".format(sectionname, coll_name))
                pool = self._mongo_pools[pool_name]
                coll = pool.get_collection(coll_name)
                self._mongo_colls[sectionname] = coll
                self.log.debug("setting up mongodb collection {0} done".format(sectionname))
        self.log.info("setting up mongodb collections done")

    @property
    def config(self):
        return self._config

    @property
    def config_dict(self):
        return self._config_dict

    @property
    def pid(self):
        return self._pid

    @property
    def nodaemon(self):
        return self._nodaemon

    def create_admin(self):
        self.config.read_file(open(self._config_file))
        self._config_dict = self._cfg_to_dict(self.config)
        self._setup_pools()
        self._setup_colls()

        admin = {
            "_id": "default_admin",
            "admin": True,
            "email": "admin@example.com",
            "name": "Default Admin User",
            "password": "password"
        }

        m_users = Users(self._mongo_colls['users'])
        m_users.create(admin)

    def manage_indices(self):
        self.config.read_file(open(self._config_file))
        self._config_dict = self._cfg_to_dict(self.config)
        self._setup_pools()
        self._setup_colls()

        sessions = self._mongo_colls['sessions']
        sessions.create_index([('lastused', pymongo.ASCENDING)], expireAfterSeconds=3600)
        lostpw = self._mongo_colls['lostpw']
        lostpw.create_index([('created', pymongo.ASCENDING)], expireAfterSeconds=3600)

    def quit(self):
        try:
            pid = open(self.pid).readline()
        except IOError:
            print("Daemon already gone, or pidfile was deleted manually")
            sys.exit(1)
        print("terminating Daemon with Pid: {0}".format(pid))
        os.kill(int(pid), signal.SIGTERM)
        sys.stdout.write("Waiting...")
        while os.path.isfile(self.pid):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(0.5)
        print("Gone")

    def start(self, devel=False):
        self.config.read_file(open(self._config_file))
        self._config_dict = self._cfg_to_dict(self.config)
        try:
            jsonschema.validate(self.config_dict['main'], CHECK_CONFIG_MAIN)
        except jsonschema.exceptions.ValidationError as err:
            print("main section: {0}".format(err))
            sys.exit(1)
        if devel:
            self._app(devel=True)
            return
        daemon = DaemonContext(pidfile=PidFile(self.pid))
        if self.nodaemon:
            daemon.detach_process = False
        dlog = open(self.config.get('main', 'dlog'), 'w')
        daemon.stderr = dlog
        daemon.stdout = dlog
        daemon.open()
        self._app()
