"""
Bitbucket tools.
"""

import os
import requests

BUILD_STATUS_STARTED = 'INPROGRESS'
BUILD_STATUS_STOPPED = 'SUCCESSFUL'
BUILD_STATUS_FAILURE = 'FAILED'

URL='https://api.bitbucket.org/2.0/repositories/%s/commit/%s/statuses/build'

def get_url():
    "Build the URL"
    _ = URL % (os.environ['CI_REPO_NAME'], os.environ['CI_COMMIT_ID'])
    return _

def get_build_data(state):
    "Get the build data"
    _ = {'state':state,
         'key':os.environ['CI_NAME'],
         'name':os.environ['CI_BUILD_NUMBER'],
         'url':os.environ['CI_BUILD_URL']}
    return _

def _build_info(state):
    "Upload build status."
    url = get_url()
    data = get_build_data(state)
    auth = (os.environ['BB_USERNAME'], os.environ['BB_PASSWORD'])
    post = requests.post(url, json=data, auth=auth)
    # An unsuccessful status post should not stop a build
    if post.status_code != 200:
        print('# Bitbucket POST error:', post.status_code, post.reason)

def build_started():
    "Build has started"
    _build_info(BUILD_STATUS_STARTED)

def build_stopped():
    "Build has started"
    _build_info(BUILD_STATUS_STOPPED)

def build_failure():
    "Build has started"
    _build_info(BUILD_STATUS_FAILURE)
    raise SystemExit(1)

