from dashboard.settings import *

#TODO: Check if this file is getting included in the hidash package. 
#This file should not get included in package.

# Test runner with no database creation
TEST_RUNNER = 'hidash.tests.NoDbTestRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'politica',
        'USER': 'hiway',
        'PASSWORD': 'hiway',
        'HOST': 'localhost',  # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    },
    'hiway': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hiway',
        'USER': 'hiway',
        'PASSWORD': 'hiway',
        'HOST': 'localhost',  # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    },
}
HIDASH_SETTINGS = {
    'parameter_processors': [
        processors.add_loggedin_user,
    ], 'xml_file_path': "/home/hasher/apps/hidash/hidash/test_charts.xml"

}
