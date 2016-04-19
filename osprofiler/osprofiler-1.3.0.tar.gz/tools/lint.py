# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Intel Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Zhongyue Luo, Intel Corporation.
#

import sys

from pylint import lint


ENABLED_PYLINT_MSGS = ['W0611']


def main(dirpath):
    enable_opt = '--enable=%s' % ','.join(ENABLED_PYLINT_MSGS)
    lint.Run(['--reports=n', '--disable=all', enable_opt, dirpath])

if __name__ == '__main__':
    main(sys.argv[1])
