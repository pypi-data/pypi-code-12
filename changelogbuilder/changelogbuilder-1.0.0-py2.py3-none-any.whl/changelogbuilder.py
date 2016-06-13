#!/usr/bin/env python
import re
import os
import git
import sys

def main():
    semver_pattern = '(?:(\d+)\.)(?:(\d+)\.)(?:(\d+))'
    
    BASE_DIR = os.getcwd()
    g = git.cmd.Git(BASE_DIR)
    commits = list(filter(None, g.log("--format=%B").splitlines()))
    
    output = ''
    for commit in commits:
        search = re.search(semver_pattern, commit)
        if bool(search):
            version = '.'.join([n for n in search.groups()])
            output += '\n\n'
            output += "== " + version + '\n'
            output += '\n'
        else:
            output += '  * ' + commit + '\n'
    
    print(output)

if __name__ == "__main__":
    main()
