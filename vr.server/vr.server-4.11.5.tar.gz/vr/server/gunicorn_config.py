# Config file for passing in on the gunicorn command line.
import os
import importlib


bind = '0.0.0.0:' + str(os.environ.get('PORT', 8000))
name = 'velociraptor_web'
workers = 4
worker_class = "gevent"  # automatically does a gevent.monkey.patch_all()
loglevel = 'info'


def def_post_fork(server, worker):
    importlib.import_module('psycogreen.gevent').patch_psycopg()
    worker.log.info("Made Psycopg Green")


post_fork = def_post_fork
