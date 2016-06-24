"""
Relevant constants that should be changed:
- HOSTNAME (localhost for dev)
"""
# redis namespace
PREFIX = "gwsstest"

#REDIS_HOSTNAME = "203.117.155.186"
REDIS_HOSTNAME = "public.gwssqueue.garenanow.com"

SSDB_HOSTNAME = "122.11.129.72"
PORT = 8888

# Log files and pid files
LOG_FOLDER = "/var/www/gwss_parser"
PID_FOLDER = "/var/www/gwss_parser"

CONFIG = "config"
PATTERN = "pattern"
ACCESS = "access"
ALIAS = "alias" 
URLSET = "urlset"
URLCOUNT = "urlcount"
MACHINEID = "ID"
IPALIAS = "ipalias"
SERVERIP = "serverip"
MESSAGE_QUEUE = "mqueue"

SLEEP = 0.5  # tail sleep frequency
PARSER_UPDATE = 600  # parser check for update

# redis namespace for auto-update component
# not using at the moment
FILTER_JSON = "filter_json"
TIME_JSON = "time_json"
