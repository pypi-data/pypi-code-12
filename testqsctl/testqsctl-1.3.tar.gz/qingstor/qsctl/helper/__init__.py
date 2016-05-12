# =========================================================================
# Copyright (C) 2016 Yunify, Inc.
# -------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================

import os

from qingstor.qsctl.utils import is_windows

class HelpRenderer(object):

    def __init__(self, command):
        self.command = command

    def render(self):
        if is_windows():
            self.render_text_page()
        else:
            self.render_man_page()

    def render_text_page(self):
        current_path = os.path.split(os.path.realpath(__file__))[0]
        text_path = "text_pages\\%s.txt" % self.command
        text_page = os.path.join(current_path, text_path)
        cmd = "more %s" % text_page
        os.system(cmd)

    def render_man_page(self):
        current_path = os.path.split(os.path.realpath(__file__))[0]
        man_path = "man_pages/%s.1" % self.command
        man_page = os.path.join(current_path, man_path)
        cmd = "man %s" % man_page
        os.system(cmd)
