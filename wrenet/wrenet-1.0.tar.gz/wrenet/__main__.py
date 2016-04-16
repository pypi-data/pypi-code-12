#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2016 graypawn <choi.pawn@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
import wrenet
from wrenet.wrenet import Interfaces


parser = argparse.ArgumentParser()
parser.add_argument('directory',
                    help='The directory included Windows registrys')
parser.add_argument('--version', action='version',
                    version='%(prog)s ' + wrenet.__version__)
parser.add_argument('-r', '--root', action='store_true',
                    help='Use the Windows mount point as directory')
args = parser.parse_args()


def main():
    if args.root == True:
        args.directory = args.directory + "/Windows/System32/config"
    try:
        Interfaces(args.directory).printAll()
    except wrenet.wrenet.InvalidRegistryFile as e:
        print("%s: %s %s" % (parser.prog, args.directory, e.args[0]))
    except Exception as e:
        print("%s: %s: %s" % (parser.prog, args.directory, e.args[1]))


if __name__ == "__main__":
    main()
