"""bsw - Build Static Website

A simple static website generator operating on the current directory and
building static websites from pages and templates.

Your project folder should be structured as follows:
    pages/
    templates/
        base.html

An example layout would be:
    pages/
        about/
            index.html
        index.html
    templates/
        static/
            site_logo.png
        includes/
            social_media_links.html
        base.html
        blog.html
    static/
        images/
            blog_header_20160101.png


This example has a base template (base.html), a blog template (blog.html),
an includes file with social media links (social_media_links.html),
and default site page (index.html) and an about page (about/index.html).

Static files from both the site statics (static/) and template statics
(templates/static/) folders are combined into the build/ folder
(automatically created when the site is first generated).

The structure in pages/ is preserved and cloned to the build/ folder.
"""

import argparse
import os

try:
    # Python 3
    import http.server
    import socketserver
except ImportError:
    # Python 2
    import SimpleHTTPServer
    import SocketServer

import sys

from . import files
from . import pages
from . import templates

OUT_DIR = os.path.abspath(os.path.join(".", "build"))


def serve_content():
    """Serve rendered content on SimpleHTTPServer. This helps with absolute
    file paths such as /static/css/main.css, which wouldn't work
    properly if opened directly in from file:///"""
    PORT = 8000
    os.chdir(OUT_DIR)

    # Allow us to quickly kill and restart server without waiting for TCP
    # socket to close down completely
    try:
        # Python 3
        handler = http.server.SimpleHTTPRequestHandler
        socketserver.TCPServer.allow_reuse_address = 1
        httpd = socketserver.TCPServer(("", PORT), handler)
    except NameError:
        # Python 2
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        SocketServer.TCPServer.allow_reuse_address = 1
        httpd = SocketServer.TCPServer(("", PORT), handler)

    print("Serving content at localhost: " + str(PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit()


def build_static_web(clean_build_path):
    file_manager = files.FileManager(OUT_DIR)

    # Check that required paths (e.g. base template) exist before starting
    try:
        file_manager.check_required_paths()
    except IOError as ex:
        print("Error: {0}".format(ex))
        print("Did you remember to create the 'templates' folder and "
              "'base.html' template?")
        sys.exit(1)

    if (clean_build_path):
        print("Cleaning build path...")
        file_manager.clean_build_path()
    file_manager.create_out_dir()

    print("Loading pages...")
    site_pages = pages.collect_pages()
    for page in site_pages:
        page.load_and_parse()

    # Check that any explicit templates exist before rendering
    try:
        templates.check_templates_exist(site_pages)
    except IOError as ex:
        print("Error: {0}".format(ex))
        sys.exit(1)

    print("Rendering pages...")
    for page in site_pages:
        page.render()
    print("Writing pages...")
    pages.write_pages(site_pages, OUT_DIR)

    print("Copying site and template assets...")
    file_manager.copy_template_assets()
    file_manager.copy_site_assets()

    print("Static site build complete.")


def main():
    parser = argparse.ArgumentParser(
        description="bsw - build static website")
    parser.add_argument("-C", "--clean", action="store_true",
                        help="remove existing build folder before building")
    parser.add_argument("-s", "--http-server", action="store_true",
                        help="serve content after build (default port 8000)")
    args = parser.parse_args()

    clean_build_path = False
    if args.clean:
        clean_build_path = True

    build_static_web(clean_build_path)

    if args.http_server:
        serve_content()
