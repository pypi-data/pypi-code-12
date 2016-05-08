#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""sorno_locate_git gets the remote location of a local file/directory from a
local git repository.


    Copyright 2016 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
import os
import sys


class App(object):
    def __init__(self, args):
        self.args = args

    def run(self):
        loc = self.args.file_or_dir
        if not loc:
            loc = "."

        loc_path = os.path.abspath(loc)

        if os.path.isdir(loc_path):
            path = loc_path
        else:
            path = os.path.dirname(loc_path)

        # find git config file
        git_config_file = None
        # The local root directory of your local repo, e.g. /User/user1/mygit
        root_dir = None
        while path and path != "/":
            if ".git" in os.listdir(path):
                root_dir = path
                git_dir = os.path.join(path, ".git")
                if "config" in os.listdir(git_dir):
                    git_config_file = os.path.join(git_dir, "config")
                    break

            path = os.path.dirname(path)

        if not git_config_file:
            print("Cannot find git config file", file=sys.stderr)
            return 1

        prefix = "url = "
        with open(git_config_file) as file_obj:
            for line in file_obj:
                line = line.strip()
                if line.startswith(prefix):
                    # E.g. found "http://github.com/xxx/yyy" in the git config
                    # file
                    git_repo_url = line[len(prefix):]
                    # E.g. /User/user1/mygit/my/awesome/file becomes
                    # my/awesome/file
                    relative_path = loc_path[len(root_dir):].lstrip("/")
                    if relative_path and "github.com" in git_repo_url:
                        relative_path = os.path.join(
                            "tree/master",
                            relative_path,
                        )
                    remote_loc = os.path.join(
                        # take out .git from the end
                        git_repo_url[:-4],
                        relative_path,
                    )

                    remote_loc = remote_loc.rstrip("/")
                    # found it!
                    print(remote_loc)
                    return 0

        print("Cannot find the remote url", file=sys.stderr)
        return 1


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2016")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file_or_dir", nargs="?")

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    app = App(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
