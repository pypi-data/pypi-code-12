# Copyright 2015 Joe H. Rahme <joehakimrahme@gmail.com>
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
import os


APP_TEMPLATE = """import os

from blogstrap import create_app

BASE = os.path.dirname(os.path.abspath(__file__))
config = lambda x: os.path.join(BASE, x)

application = create_app(config('.blogstrap.conf'))

if __name__ == '__main__':
    application.run()
"""

CONF_TEMPLATE = """# The domain name of your blog
SERVERNAME=""
# The path of a directory that holds the markdown articles
BLOGROOT = "articles"
# The title will be added to the top banner in every page
BLOGTITLE = "Generated with BlogStrap"
# Find out which themes are available here: http://strapdownjs.com/
THEME = "simplex"
# Make the app more verbose when necessary. Don't use in production.
DEBUG = True
"""


def build(args):
    app_path = os.path.join(args.target, 'wsgi.py')
    conf_path = os.path.join(args.target, '.blogstrap.conf')
    blogroot_path = os.path.join(args.target, "articles")

    if not os.path.exists(args.target):
        os.makedirs(args.target)

    if not os.path.exists(blogroot_path):
        os.makedirs(blogroot_path)

    with open(app_path, 'w') as f:
        f.write(APP_TEMPLATE)

    with open(conf_path, 'w') as f:
        f.write(CONF_TEMPLATE)
