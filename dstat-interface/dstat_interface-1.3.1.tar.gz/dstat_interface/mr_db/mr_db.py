#!/usr/bin/env python
import os
from os.path import expanduser
import time
import logging
import atexit
import signal
from uuid import uuid4, UUID

import psutil
from psutil import Popen
import ZODB, ZODB.FileStorage
from ZEO import ClientStorage
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
import transaction
from persistent import Persistent
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

root_logger = logging.getLogger("mr_db")
root_logger.setLevel(level=logging.INFO)
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter(
                    fmt='%(asctime)s [%(name)s](%(levelname)s) %(message)s',
                    datefmt='%H:%M:%S'
                )
log_handler.setFormatter(log_formatter)
root_logger.addHandler(log_handler)
logging.getLogger('ZODB').addHandler(log_handler)
logging.getLogger('ZEO').addHandler(log_handler)
logger = logging.getLogger(__name__)

package_directory = os.path.dirname(os.path.abspath(__file__))
conf_file = os.path.join(package_directory, 'server_conf.xml')

process = None

class InputError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class KeyExistsError(InputError):
    """Exception raised when trying to add a db key that already exists.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """
    pass
        
class Patient(Persistent):
    """class for patient data storage. Each application should write data as
    experiment entries, defining their own data storage objects. N.B. if
    classes are used to store data, class definitions must be available when
    retrieving object.
    ----
    Arguments:
    pid: patient id (should be the same as db key)---If not provided, 
         will use -1 (Negative PIDs are reserved for non-patient use).
    kwargs: additional keyword arguments that will be saved in metadata dict.
    """
    def __init__(self, pid=-1, **kwargs):
        if pid is None:
            raise InputError(pid, "No ID provided")
        self.id = pid
        self.metadata = PersistentMapping(kwargs)
        self.experiments = OOBTree()
    
    def link_experiment(self, db, uuid):
        """Hard links an experiment with uuid from db. db should be a OOBTree
        or PersistentMapping already in the ZODB.
        """
        
        self.experiments[uuid] = db[uuid]
   
class DbConnection(object):
    """Class for DB connection. Multiple threads/processes can access db 
    simultaneously, but each must have its own connection. Must call commit
    method to save data to database. Throws ClientStorage.ClientDisconnected
    if connection can't be made.
    ----
    Arguments:
    port: port to connect to
    """
    def __init__(self, port=9998, root_dir=None):
        addr = ('localhost', port)
        
        if root_dir is None:
            root_dir = expanduser('~/.mr_db')
        
        root_dir = expanduser(root_dir)
        
        full_path = os.path.abspath("%s/data/blob" % root_dir)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            
        self.storage = ClientStorage.ClientStorage(addr,
                        blob_dir="%s/data/blob" % root_dir,
                        shared_blob_dir=True,
                        client_label='dstat-interface',
                        max_disconnect_poll=4,
                        wait=False,
                        wait_timeout=5
                        )

        self.db = ZODB.DB(self.storage)
        self.connection = self.db.open()
        self.databases = self.connection.root()
        
        if not self.databases.has_key('patients'):
            self.databases['patients'] = OOBTree()

        self.patients = self.databases['patients']
    
    def commit(self):
        transaction.commit()
    
    def abort(self):
        transaction.abort()
        
def start_server(root_dir=None, port=9998,
        conf_file=conf_file):
    
    if root_dir is None:
        root_dir = expanduser('~/.mr_db')
    else:
        root_dir = expanduser(root_dir)
    data_dir = "%s/data" % root_dir
    log_dir = "%s/logs" % root_dir
    pid_file = "%s/zeo.pid" % root_dir
    
    full_path = os.path.abspath(data_dir)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    
    full_path = os.path.abspath(log_dir)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    
    global pid_f
    pid_f = pid_file
    
    if os.path.isfile(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.readline().strip())
        
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                p.terminate()
                p.wait(timeout=3)
                if p.is_running():
                    p.kill()
        except ValueError:
            pass
            
    global logfile
    logfile = open('%s/zeo.log' % log_dir, 'w')
    
    global process
    process = Popen(['python', '-m', 'ZEO.runzeo', '-C', conf_file],
                    env=dict(os.environ, PORT=str(port), DATA_DIR=data_dir),
                    stdout=logfile,
                    stderr=logfile
                    )
    
    with open(pid_file, 'w') as f:
        f.write(str(process.pid))
    
    atexit.register(stop_server) # Make sure server is cleaned up on quit
              
    return process
                 
def stop_server():
    global process
    
    if process is not None:
        if process.is_running():
            process.terminate()
            process.wait(timeout=3)
        if process.is_running():
            process.kill()
            process.wait()
        process = None

if __name__ == '__main__':
    start_server()    