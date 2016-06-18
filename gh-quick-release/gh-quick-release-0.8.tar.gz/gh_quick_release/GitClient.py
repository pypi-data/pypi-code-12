from subprocess import call, check_output, STDOUT
from os import devnull


class GitClient:
    def __init__(self, redirect, no_verify=True):
        self.redirect = redirect
        self.no_verify = no_verify

    def _arr(self, tpl):
        arr = []
        for item in tpl:
            arr.append(item)
        return arr

    def check_output(self, *params):
        args = self._arr(('git',) + params)
        return check_output(args)

    def status(self, *params):
        args = self._arr(('git', 'status') + params)
        return check_output(args)

    def call(self, params):
        args = self._arr(('git',) + params)

        code = 0
        if not self.redirect:
            code = call(args)
        else:
            with open(devnull, 'w') as n:
                code = call(args, stdout=n, stderr=STDOUT)
        if code != 0:
            cmd = ' '.join(args)
            raise RuntimeError('Git command "' + cmd + '" failed')

    def push(self, *params):
        self.call(('push',) + params)

    def pull(self, *params):
        self.call(('pull',) + params)

    def commit(self, *params):
        if self.no_verify:
            self.call(('commit',) + params + ('--no-verify',))
        else:
            self.call(('commit',) + params)

    def add(self, *params):
        self.call(('add',) + params)

    def checkout(self, *params):
        self.call(('checkout',) + params)

    def merge(self, *params):
        self.call(('merge',) + params)

    def fetch(self, *params):
        self.call(('fetch',) + params)

    def current_branch(self):
        output = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        return output.replace('\n', '')
