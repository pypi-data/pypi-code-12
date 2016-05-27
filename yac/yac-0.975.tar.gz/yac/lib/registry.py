import redis   # for remote registry
import shelve  # for local registry
import os
import fakeredis # for mock registry (unit testing)
from os.path import expanduser

from yac.lib.paths import get_config_path

# the url and port for the yac registry in redis
PUBLIC_REGISTRY = {"host": "pub-redis-14705.us-east-1-3.4.ec2.garantiadata.com",
                    "port": 14705 }

PRIVATE_REGISTRY_DB_KEY = 'private_registry'

MOCK_REGISTRY_HOST = "MOCK"
MOCK_REGISTRY_DESC = {"host": MOCK_REGISTRY_HOST, "port":"n/a"}

class RegError():
    def __init__(self, msg):
        self.msg = msg

def _get_registry():
   
    # if a private registry has been configured
    private_registry = get_local_value(PRIVATE_REGISTRY_DB_KEY)

    if (private_registry and 'host' in private_registry and
        private_registry['host'] != MOCK_REGISTRY_HOST):
        registry = redis.Redis(host=private_registry['host'], port=private_registry['port'])
    elif (private_registry and 'host' in private_registry and
        private_registry['host'] == MOCK_REGISTRY_HOST): 
        # use a redis mock for the registry, typically for unit testing
        registry = fakeredis.FakeStrictRedis()       
    else:
        registry = redis.Redis(host=PUBLIC_REGISTRY['host'], port=PUBLIC_REGISTRY['port'])

    return registry

def get_registry_keys():

    registry = _get_registry()

    return registry.keys()

def set_remote_string_w_challenge(key_name, string_value, challenge_phrase=""):

    original_challenge = ""

    already_registered = get_remote_value(key_name)

    # see if value is already set
    if already_registered:

        # get the original challenge phrase
        original_challenge = _get_remote_challenge(key_name)

    if not challenge_phrase:
        # prompt use for a phrase
        challenge_phrase = raw_input("Enter your challenge phrase >> ")

    # set the value in the registry if 
    # 1) value is not already registered, or 
    # 2) the challenge phrase matches
    if (not already_registered or challenge_phrase == original_challenge):

        value = {"challenge": challenge_phrase, "value": string_value}
        registry = _get_registry()

        registry.hmset(key_name, value)
    else:
        print key_name, original_challenge

        raise RegError("challenge phrase mismatch") 

def get_remote_value(key_name):

    registry = _get_registry()

    entry = registry.hgetall(key_name)

    if (entry and type(entry)==dict):       
        return entry['value']    
    elif entry:
        return entry
    else:
        return ""

def _get_remote_challenge(key_name):

    registry = _get_registry()

    entry = registry.hgetall(key_name)

    if entry:        
        return entry['challenge']    
    else:
        return ""        

def clear_entry_w_challenge(key_name, challenge_phrase=""):

    original_challenge = ""

    already_registered = get_remote_value(key_name)

    # see if value is already set
    if already_registered:

        # get the original challenge phrase
        original_challenge = _get_remote_challenge(key_name)

    if not challenge_phrase:
        # prompt use for a phrase
        challenge_phrase = raw_input("Enter your challenge phrase >> ")

    # clear the value in the registry if 
    # 1) value is not already registered, or 
    # 2) the challenge phrase matches
    if (not already_registered or challenge_phrase == original_challenge):

        _delete_registry_value(key_name)
    else:
        raise RegError("challenge phrase mismatch")    

def _delete_registry_value(key_name):

    print 'clearing %s'%key_name
    
    registry = _get_registry()

    registry.delete(key_name)

def set_local_value(key_name, value):

    # save value to shelve db
    yac_db = _get_local_db()

    yac_db[key_name] = value

def get_local_value(key_name):  

    local_db = _get_local_db()

    if key_name in local_db:
        return local_db[key_name]
    else:
        return ""

def delete_local_value(key_name):   

    local_db = _get_local_db()

    if key_name in local_db:
        local_db.pop(key_name)

def get_local_keys():

    local_db = _get_local_db()

    return local_db.keys()        

def set_private_registry(private_registry_desc):

    if private_registry_desc:

        print "saving private registry setting"

        # save vpc preferences to local db
        set_local_value(PRIVATE_REGISTRY_DB_KEY,private_registry_desc)

def get_private_registry():

    # get registry currently configured
    return get_local_value(PRIVATE_REGISTRY_DB_KEY)   

def clear_private_registry():

    set_local_value(PRIVATE_REGISTRY_DB_KEY,{})

def _get_local_db():

    # local DB should be saved under the user's home directory
    home = expanduser("~")
    db_home = os.path.join(home,'.yac')

    if not os.path.exists(db_home):
        os.makedirs(db_home)

    yac_db_path = os.path.join( db_home,'yac_db')

    local_db = shelve.open(yac_db_path)

    return local_db
