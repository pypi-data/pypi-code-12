"""
Get Application Credentials as json.
"""
import os
import json
import time

from oauth2client.client import GoogleCredentials

from dfp_sync.utils import parse_gcloud_config


def setup(parser):
  """
  Arguments for the service command.
  """
  srv_parser = parser.add_parser("cloud-auth", 
    help="Get you gcloud authentication parameters as json. "
    "Must have google cloud SDK installed. You'll need this "
    "file to run $ dfp-sync transfer-file")
  return 'cloud-auth', run


def run(opts):
  """
  Get authentications via browser auth flow
  """
  os.system('gcloud auth login  > /dev/null')
  time.sleep(1)
  creds = GoogleCredentials.get_application_default()
  raw =  json.loads(creds.to_json())
  print(json.dumps(parse_gcloud_config(raw)))