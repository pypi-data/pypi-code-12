"""
Coveralls API for Bitbucket
"""
import json
import hashlib
import requests
from coverage import __version__ as coverage_version
# coverage 3 and 4 have api changes, since I use pydev which is still stuck
# on coverage 3, but the rest of the world has moved on I'll need to support
# both.
from coverage import coverage as Coverage

BASE='https://coveralls.io'
CLIENT='coveralls-python-hg'
_API='api/v1/jobs'

def _generate_source_files(file_path_name='.coverage', strip_path=None):
    "Use the .coverage data file to generate the coverage lines for coveralls."
    coverage = Coverage(data_file=file_path_name)
    coverage.load()

    tmp = list()

    for file_name in coverage.data.measured_files():
        analysis = coverage._analyze(file_name)# pylint:disable=protected-access
        # pylint:disable=no-member
        if coverage_version.startswith('3'): # pragma: no cover
            length = len(analysis.parser.lines) + 1
            md5 = hashlib.md5(analysis.parser.text.encode('UTF-8')).hexdigest()
        else: # pragma: no cover
            source = analysis.file_reporter.source()
            md5 = hashlib.md5(source.encode('UTF-8')).hexdigest()
            length = len(source.split('\n'))
        lines = list()
        for line_no in range(1, length):
            if line_no in analysis.missing:
                lines.append(0)
            elif line_no in analysis.statements:
                lines.append(1)
            else:
                lines.append(None)

        if strip_path is not None:
            if file_name.startswith(strip_path):
                file_name = file_name[len(strip_path):]

            if file_name.startswith('/'):
                file_name = file_name[1:]

        tmp.append({'name':file_name,
                    'source_digest':md5,
                    'coverage':lines})

    return tmp


def _fetch_json_data(url):
    "Return the json data"
    got = requests.get(url)
    if got.status_code != 200:
        got.raise_for_status()

    data = got.json()
    return data


class API(object):
    """API Front-end to coveralls.io
    At the moment only fetching builds and submitting builds is supported.
    """
    def __init__(self, user, repo, token, dvcs='bitbucket'):
        self.settings = {'USER':user, 'REPO':repo, 'TOKEN':token,
                         'BASE':BASE, 'DVCS':dvcs, 'FORM':'json',
                         'UPLOAD':dict()}
        self.url_post = '/'.join([BASE, _API])

    def _url(self, *keys, add_form=False):
        "Build the url using the settings and keys."
        #If a key is not in the settings, it will be included as the key itself.
        tmp = list()
        for key in keys:
            if key in self.settings:
                tmp.append(self.settings[key])
            else:
                tmp.append(key)
        url = '/'.join(tmp)
        if add_form:
            url = url + '.' + self.settings['FORM']
        return url

    def list_builds(self):
        "Yields all builds, newest first."
        url = self._url('BASE', 'DVCS', 'USER', 'REPO', add_form=True)
        url = url + '?page='
        page = 0
        while True:
            page += 1
            data = _fetch_json_data(url + str(page))

            for build in data['builds']:
                yield build

            if len(data['builds']) == 0:
                break

    def builds(self, commit_sha):
        "Return builds (singular for list_builds)."
        url = self._url('BASE', 'builds', commit_sha, add_form=True)
        data = _fetch_json_data(url)
        return data

    def _add_values(self, dictionary):
        ""
        for key, value in dictionary.items():
            if value is not None:
                self.settings['UPLOAD'][key] = value

    def set_repo_token(self, token=None):
        "Set the coveralls repository token"
        if token is None:
            token = self.settings['TOKEN']

        self.settings['UPLOAD']['repo_token'] = token


    def set_service_values(self, name=CLIENT, number=None, job_id=None):
        "Set service values."
        tmp = {'service_name':name, 'service_number':number,
               'service_job_id':job_id}
        self._add_values(tmp)

    def set_build_values(self, build_url=None, branch=None, pull_request=None):
        "Set build values."
        if pull_request.strip().lower() == 'false':
            pull_request=None
        tmp = {'service_build_url':build_url, 'service_branch':branch,
               'service_pull_request':pull_request}
        self._add_values(tmp)

    def set_source_files(self, coverage_file, strip_path=None):
        "set the source files"
        self.settings['UPLOAD']['source_files'] = \
                               _generate_source_files(coverage_file, strip_path)

    def _assert_git_dict(self):
        "Make sure the git headers are set."
        if 'git' not in self.settings['UPLOAD']:
            self.settings['UPLOAD']['git'] = {'head':dict()}

    def set_dvcs_user(self, name_author, email_author,
                     name_committer=None, email_comitter=None):
        "Set repository user details."
        self._assert_git_dict()
        if name_committer is None:
            name_committer = name_author
        if email_comitter is None:
            email_comitter = email_author

        tmp = {'author_name':name_author, 'author_email':email_author,
               'commiter_name':name_committer, 'committer_email':email_comitter}

        for key, value in tmp.items():
            self.settings['UPLOAD']['git']['head'][key] = value


    def set_dvcs_commit(self, commit_id, message, branch, remotes=None):
        "set repository commit details."
        self._assert_git_dict()
        upload = self.settings['UPLOAD']
        upload['git']['head']['id'] = commit_id
        upload['git']['head']['message'] = message
        upload['git']['branch'] = branch

        if remotes is not None:
            upload['git']['remotes'] = remotes

    def _check_upload(self):
        upload = self.settings['UPLOAD']
        tmp = ['set_source_files', 'set_dvcs_user', 'set_dvcs_commit']

        if 'service_name' not in upload:
            self.set_service_values()

        if 'repo_token' not in upload:
            self.set_repo_token()

        if 'source_files' in upload:
            tmp.remove('set_source_files')

        if 'git' not in upload:
            tmp.remove('set_dvcs_user')
            tmp.remove('set_dvcs_commit')
        else:
            if 'author_name' in upload['git']['head']:
                tmp.remove('set_dvcs_user')

            if 'id' in upload['git']['head']:
                tmp.remove('set_dvcs_commit')

        if len(tmp) > 0:
            text = 'Missing upload data, please set data with: %s' % str(tmp)
            raise ValueError(text)

        return upload

    def upload_coverage(self):
        "Upload coverage data."
        self._check_upload()
        json_file = json.dumps(self.settings['UPLOAD'])
        files = {'json_file':json_file}
        post = requests.post(self.url_post, files=files)
        if post.status_code != 200:
            post.raise_for_status()
        else:
            return True

