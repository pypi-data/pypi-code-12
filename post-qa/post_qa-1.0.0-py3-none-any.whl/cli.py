"""Command line interface / runner."""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import sys
import argparse
import json

import requests

from . import jsonshim
from . import lsstsw
from . import jenkinsenv


def run_post_qa():
    """CLI entrypoint for the ``post-qa`` command."""
    args = parse_args()

    # Shim validate_drp's JSON to SQuaSH measurements format
    with open(args.qa_json_path) as f:
        qa_json = json.load(f, encoding='utf-8')
    job_json = jsonshim.shim_validate_drp(qa_json)

    # Add 'packages' sub-document
    lsstsw_install = lsstsw.Lsstsw(args.lsstsw_dirname)
    job_json.update(lsstsw_install.json)

    # Add metadata from the CI environment
    jenkins = jenkinsenv.JenkinsEnv()
    job_json.update(jenkins.json)

    print(json.dumps(job_json, indent=2, sort_keys=True))
    upload_json(job_json, api_url=args.api_url,
                api_user=args.api_user, api_password=args.api_password)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--lsstsw',
        dest='lsstsw_dirname',
        required=True,
        help='Path of lsstsw directory')
    parser.add_argument(
        '--qa-json',
        dest='qa_json_path',
        required=True,
        help='Filename of QA JSON output file')
    parser.add_argument(
        '--api-url',
        dest='api_url',
        required=True,
        help='URL of SQuaSH API endpoint for job submission')
    parser.add_argument(
        '--api-user',
        dest='api_user',
        required=True,
        help='Username for SQuaSH API')
    parser.add_argument(
        '--api-password',
        dest='api_password',
        required=True,
        help='Password for SQuaSH API')
    return parser.parse_args()


def upload_json(job_json, api_url, api_user, api_password):
    """Upload Job json document to SQuaSH through POST /api/jobs/ endpoint."""
    r = requests.post(api_url, auth=(api_user, api_password), json=job_json)
    print(r.status_code)
    if r.status_code != 201:
        print(r.json())
        sys.exit(1)
