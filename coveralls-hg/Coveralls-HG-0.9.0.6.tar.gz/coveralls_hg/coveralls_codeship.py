"""
Use the codeship environmental variables to fill in the right values to upload
to coveralls.
"""
from pprint import pprint
from copy import deepcopy
import os
from coveralls_hg.api import API

# pylint:disable=dangerous-default-value
def main(env=os.environ, coverage_file='.coverage'):
    "main script"
    user, repo = env['CI_REPO_NAME'].split('/')
    api = API(user,repo, token=env['COVERALLS_REPO_TOKEN'])

    api.set_build_values(build_url=env['CI_BUILD_URL'], branch=env['CI_BRANCH'],
                         pull_request=env['CI_PULL_REQUEST'])

    api.set_dvcs_commit(commit_id=env['CI_COMMIT_ID'],
                        message=env['CI_MESSAGE'], branch=env['CI_BRANCH'])

    api.set_dvcs_user(name_author=env['CI_COMMITTER_NAME'],
                      email_author=env['CI_COMMITTER_EMAIL'])

    api.set_service_values(number=env['CI_BUILD_NUMBER'])

    cwd = os.path.abspath(os.getcwd())
    api.set_source_files(coverage_file, strip_path=cwd)

    print('# Uploading to coveralls.io using the following configuration:')
    copied = deepcopy(api.settings['UPLOAD'])
    source = copied.pop('source_files')
    pprint(copied)
    print('# Coverage:')
    for item in source:
        print(item['source_digest'], '|', item['name'])
        tmp = [str(value) if value in [0,1] else '-' for value in item['coverage']]
        print(''.join(tmp))
    api.upload_coverage()
    print('# Upload done.')


if __name__ == '__main__': # pragma: no cover
    main()
