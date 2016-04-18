# Copyright 2014 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# CONSTANTS MODULE
MIN_TMOS_MAJOR_VERSION = 11
MIN_TMOS_MINOR_VERSION = 5
MIN_EXTRA_MB = 500
DEFAULT_HOSTNAME = 'bigip1'
MAX_HOSTNAME_LENGTH = 128
DEFAULT_FOLDER = "Common"
FOLDER_CACHE_TIMEOUT = 120
CONNECTION_TIMEOUT = 30
FDB_POPULATE_STATIC_ARP = True
# DEVICE LOCK PREFIX
DEVICE_LOCK_PREFIX = 'lock_'
# DIR TO CACHE WSDLS.  SET TO NONE TO READ FROM DEVICE
# WSDL_CACHE_DIR = "/data/iControl-11.4.0/sdk/wsdl/"
WSDL_CACHE_DIR = ''
# HA CONSTANTS
HA_VLAN_NAME = "HA"
HA_SELFIP_NAME = "HA"
# VIRTUAL SERVER CONSTANTS
VS_PREFIX = 'vs'
# POOL CONSTANTS
POOL_PREFIX = 'pool'
# POOL CONSTANTS
MONITOR_PREFIX = 'monitor'
# VLAN CONSTANTS
VLAN_PREFIX = 'vlan'
# BIG-IP PLATFORM CONSTANTS
BIGIP_VE_PLATFORM_ID = 'Z100'
# DEVICE CONSTANTS
DEVICE_DEFAULT_DOMAIN = ".local"
DEVICE_HEALTH_SCORE_CPU_WEIGHT = 1
DEVICE_HEALTH_SCORE_MEM_WEIGHT = 1
DEVICE_HEALTH_SCORE_CPS_WEIGHT = 1
DEVICE_HEALTH_SCORE_CPS_PERIOD = 5
DEVICE_HEALTH_SCORE_CPS_MAX = 100
# DEVICE GROUP CONSTANTS
PEER_ADD_ATTEMPTS_MAX = 10
PEER_ADD_ATTEMPT_DELAY = 2
DEFAULT_SYNC_MODE = 'autosync'
# MAX RAM SYNC DELAY IS 63 SECONDS
# (3+6+9+12+15+18) = 63
SYNC_DELAY = 3
MAX_SYNC_ATTEMPTS = 10
# SHARED CONFIG CONSTANTS
SHARED_CONFIG_DEFAULT_TRAFFIC_GROUP = 'traffic-group-local-only'
SHARED_CONFIG_DEFAULT_FLOATING_TRAFFIC_GROUP = 'traffic-group-1'
VXLAN_UDP_PORT = 4789
