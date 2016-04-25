# file test/localsettings.py.dist
#
#   Copyright 2011 Emory University Libraries
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os

# must be set before importing anything from django
os.environ['DJANGO_SETTINGS_MODULE'] = 'localsettings'

# secret key required as of django 1.5
SECRET_KEY = 'notsomuchofasecretafterall'


# existdb 1.4
# EXISTDB_SERVER_URL = "http://kamina.library.emory.edu:8080/exist"
# existdb 2.x
# FIXME: trailing slash shouldn't be required
EXISTDB_SERVER_URL = "http://wlibqas002.library.emory.edu:8081/exist/"

# EXISTDB_SERVER_URL = 'http://server.domain.com:port/exist/'
# exist admin account must be have dba privileges
EXISTDB_SERVER_ADMIN_USER = "eulexistdb"
EXISTDB_SERVER_ADMIN_PASSWORD = "3ul3x1stdb"

# EXISTDB_SERVER_URL = "http://rodan.library.emory.edu:8080/exist/"
# EXISTDB_SERVER_URL = "https://rodan.library.emory.edu:8443/exist/"
# EXISTDB_SERVER_ADMIN_USER = "admin"
# EXISTDB_SERVER_ADMIN_PASSWORD = ""


# limited-access test account; will be created by the admin user for
# testing purposes only
EXISTDB_SERVER_USER = "eulexistdbtester"
EXISTDB_SERVER_PASSWORD = "pass1234"

EXISTDB_ROOT_COLLECTION = '/eulexistdb'
# test collection will be created and destroyed under base collection
EXISTDB_TEST_BASECOLLECTION = '/test-eulexistdb'
EXISTDB_TEST_COLLECTION = EXISTDB_TEST_BASECOLLECTION + EXISTDB_ROOT_COLLECTION


# user group will be created by admin account for permissions purposes
EXISTDB_TEST_GROUP = 'eulexistdb-test'

# default, testing
EXISTDB_SESSION_KEEP_ALIVE = False
