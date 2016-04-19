import os
import sys
import subprocess
import logging
import urllib2

import click
from destral.utils import *
from destral.testing import run_unittest_suite, get_unittest_suite
from destral.openerp import OpenERPService


logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('destral.cli')


@click.command()
@click.option('--modules', '-m', multiple=True)
@click.option('--tests', '-t', multiple=True)
def destral(modules, tests):
    sys.argv = sys.argv[:1]
    service = OpenERPService()
    if not modules:
        ci_pull_request = os.environ.get('CI_PULL_REQUEST')
        token = os.environ.get('GITHUB_TOKEN')
        if ci_pull_request and token:
            url = 'https://api.github.com/repos/{repo}/pulls/{pr_number}'.format(
                    repo=os.environ.get('CI_REPO'),
                    pr_number=ci_pull_request
                )
            req = urllib2.Request(
                url,
                headers={
                    'Authorization': 'token {0}'.format(token),
                    'Accept': 'application/vnd.github.patch'
            })
            f = urllib2.urlopen(req)
            paths = find_files(f.read())
            logger.info('Files from Pull Request: {0}: {1}'.format(
                ci_pull_request, ', '.join(paths)
            ))
        else:
            paths = subprocess.check_output([
                "git", "diff", "--name-only", "HEAD~1..HEAD"
            ])
            paths = [x for x in paths.split('\n') if x]
        modules_to_test = []
        for path in paths:
            module = detect_module(path)
            if module and module not in modules_to_test:
                modules_to_test.append(module)
    else:
        modules_to_test = modules[:]

    results = []
    addons_path = service.config['addons_path']
    for module in modules_to_test:
        install_requirements(module, addons_path)
        logger.info('Testing module %s', module)
        os.environ['DESTRAL_MODULE'] = module
        suite = get_unittest_suite(module, tests)
        result = run_unittest_suite(suite)
        if not result.wasSuccessful():
            results.append(False)
        else:
            results.append(True)
    if not all(results):
        sys.exit(1)


if __name__ == '__main__':
    destral()
