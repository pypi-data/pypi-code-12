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
import argparse
import six
if six.PY2:
    from exceptions import IOError
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

import flask

import builder


class ArticleNotFound(IOError):
    pass


class ArticleReader(object):

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        try:
            with open(self.path) as f:
                return ''.join(f.read())
        except IOError:
            raise ArticleNotFound(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class DefaultConfig(object):
    DEBUG = True
    BLOGROOT = "."
    THEME = "simplex"
    BLOGTITLE = "Powered by Blogstrap"


def create_app(config_file=None):
    app = flask.Flask(__name__)
    if config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_object(DefaultConfig)

    @app.route("/")
    def nothing():
        return "SUCCESS"

    @app.route("/<blogpost>")
    def serve_blog(blogpost):
        if blogpost.startswith("."):
            flask.abort(404)
        user_agent = flask.request.headers.get('User-Agent')
        if user_agent:
            iscurl = user_agent.lower().startswith('curl')
        else:
            iscurl = False
        root_directory = app.config['BLOGROOT']
        blogpost = "/".join((root_directory, blogpost))
        try:
            with ArticleReader(blogpost) as article:
                if iscurl:
                    return article
                else:
                    return flask.render_template("strapdown.html",
                                                 theme=app.config['THEME'],
                                                 text=article,
                                                 title=app.config['BLOGTITLE'])
        except ArticleNotFound:
            # need better support for curl
            flask.abort(404)
    return app


def build_parser():
    """Builds the argument parser."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Blogstrap commands')

    init_parser = subparsers.add_parser('init', help='Default')
    init_parser.set_defaults(which='init')
    init_parser.add_argument('-t', '--target',
                             dest='target',
                             type=str,
                             default='.',
                             help='Target folder to generate files in')

    return parser


def main():
    args = build_parser().parse_args()
    builder.build(args)

if __name__ == '__main__':
    main()
