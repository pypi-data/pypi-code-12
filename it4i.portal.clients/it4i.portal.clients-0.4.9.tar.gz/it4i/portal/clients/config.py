import ConfigParser
import os
import sys

from logger import LOGGER

default_config_path = '/usr/local/etc/it4i-portal-clients/main.cfg'
local_config_path = os.path.expanduser('~/.it4i-portal-clients/main.cfg')

config = ConfigParser.ConfigParser()
config_files = '\n'.join((4*' ' + default_config_path,
                          4*' ' + local_config_path))

try:
    config.readfp(open(default_config_path))
except IOError:
    LOGGER.warning("Default config file %s not found", default_config_path)
    if not config.read(local_config_path):
        LOGGER.error("Tried (in the following order), but no configuration found:\n%s",
                     config_files)
        sys.exit(1)

if not config.read(local_config_path):
    LOGGER.info("Local config file %s not found", local_config_path)

# mandatory configuration options
api_url = None
api_url_optname = "extranet_api_url"
try:
    api_url = config.get("main", api_url_optname)
    1/len(api_url)
except:
    LOGGER.error("""Missing or unset configuration option: %s

Suggested paths:
%s
""", api_url_optname, config_files)
    sys.exit(1)
