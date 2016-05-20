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
from pep3143daemon import DaemonContext, PidFile
import pymongo
from requestlogger import WSGILogger, ApacheFormatter
from wsgi_request_id import RequestID

# Project
from el_aap.app import app
from el_aap.controllers import *
from el_aap_api.models import *
from el_aap.models import *
from el_aap_api.errors import error_catcher


def main():
    parser = argparse.ArgumentParser(description="ElasticSearch Authentication and Authorization Proxy")

    parser.add_argument("--cfg", dest="cfg", action="store",
                        default="/etc/el_aap/el_aap.ini",
                        help="Full path to configuration")

    parser.add_argument("--pid", dest="pid", action="store",
                        default="/var/run/el_aap/el_aap.pid",
                        help="Full path to PID file")

    parser.add_argument("--nodaemon", dest="nodaemon", action="store_true",
                        help="Do not daemonize, run in foreground")

    subparsers = parser.add_subparsers(help='commands', dest='method')
    subparsers.required = True

    quit_parser = subparsers.add_parser('quit', help='Stop ElasticSearch Authentication and Authorization Proxy')
    quit_parser.set_defaults(method='quit')

    start_parser = subparsers.add_parser('start', help='Start ElasticSearch Authentication and Authorization Proxy')
    start_parser.set_defaults(method='start')

    devel_parser = subparsers.add_parser('devel', help='Start ElasticSearch Authentication and Authorization Proxy in developement mode')
    devel_parser.set_defaults(method='devel')

    parsed_args = parser.parse_args()

    if parsed_args.method == 'quit':
        el_aap = ElasticSearchAAP(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aap.quit()

    elif parsed_args.method == 'start':
        el_aap = ElasticSearchAAP(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aap.start()

    elif parsed_args.method == 'devel':
        el_aap = ElasticSearchAAP(
                cfg=parsed_args.cfg,
                pid=parsed_args.pid,
                nodaemon=parsed_args.nodaemon
        )
        el_aap.start(devel=True)


class ElasticSearchAAP(object):
    def __init__(self, cfg, pid, nodaemon):
        self._config_file = cfg
        self._config = configparser.ConfigParser()
        self._mongo_pools = dict()
        self._mongo_colls = dict()
        self._pid = pid
        self._nodaemon = nodaemon
        self.log = logging.getLogger('el_aap')

    def _acc_logging(self):
        acc_handlers = []

        try:
            access_log = self.config.get('file:logging', 'acc_log')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure the acc_log in the file:logging section')
            sys.exit(1)
        try:
            access_retention = self.config.getint('file:logging', 'acc_retention')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure the acc_retention in the file:logging section')
            sys.exit(1)
        acc_handlers.append(TimedRotatingFileHandler(access_log, 'd', access_retention))
        return acc_handlers

    def _app_logging(self):
        logfmt = logging.Formatter('%(asctime)sUTC - %(levelname)s - %(message)s')
        logfmt.converter = time.gmtime

        app_handlers = []
        try:
            aap_level = self.config.get('file:logging', 'app_loglevel')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure app_loglevel in the file:logging section')
            sys.exit(1)
        try:
            app_log = self.config.get('file:logging', 'app_log')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure app_log in the file:logging section')
            sys.exit(1)
        try:
            app_retention = self.config.getint('file:logging', 'app_retention')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure app_retention in the file:logging section')
            sys.exit(1)
        app_handlers.append(TimedRotatingFileHandler(app_log, 'd', app_retention))

        for handler in app_handlers:
            handler.setFormatter(logfmt)
            self.log.addHandler(handler)
        self.log.setLevel(aap_level)
        self.log.debug("application logger is up")

    def _app(self, devel=False):
        self._app_logging()
        self.log.info("starting up")
        self._setup_pools()
        self._setup_colls()

        try:
            host = self.config.get('elasticsearch', 'host')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure the host in the elasticsearch section')
            sys.exit(1)
        try:
            port = self.config.get('elasticsearch', 'port')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure the port in the elasticsearch section')
            sys.exit(1)
        try:
            scheme = self.config.get('elasticsearch', 'scheme')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure the scheme in the elasticsearch section')
            sys.exit(1)

        permissions = Permissions(self._mongo_colls['permissions'])
        roles = Roles(self._mongo_colls['roles'])
        users = Users(self._mongo_colls['users'])
        aa = AuthenticationAuthorization(
            users=users,
            roles=roles,
            permissions=permissions
        )

        endpoint = scheme+'://'+host+':'+port
        self.log.info("this instance is shielding {0}".format(endpoint))
        elproxy = ElasticSearchProxy(endpoint)

        app.install(MetaPlugin(aa, 'm_aa'))
        app.install(MetaPlugin(elproxy, 'm_elproxy'))
        app.install(error_catcher)

        logapp = RequestID(WSGILogger(app, self._acc_logging(), ApacheFormatter()))

        try:
            port = self.config.getint('main', 'port')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure the port in the port section')
            sys.exit(1)

        self.log.info("startup done, now serving")
        run(app=logapp, host='0.0.0.0', port=port, debug=devel, reloader=devel, server='waitress')

    def _setup_pools(self):
        self.log.info("setting up mongodb connection pools")
        for section in self.config.sections():
            if section.endswith(':mongopool'):
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
    def pid(self):
        return self._pid

    @property
    def nodaemon(self):
        return self._nodaemon

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
        if devel:
            self._app(devel=True)
        daemon = DaemonContext(pidfile=PidFile(self.pid))
        if self.nodaemon:
            daemon.detach_process = False
        dlog = open(self.config.get('main', 'dlog'), 'w')
        daemon.stderr = dlog
        daemon.stdout = dlog
        daemon.open()
        self._app()
