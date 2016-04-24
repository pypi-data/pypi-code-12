#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: flask_maple_bootstrap.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-18 16:03:01 (CST)
# Last Update: 星期五 2016-4-22 19:7:32 (CST)
#          By: jianglin
# Description:
# **************************************************************************
from flask import Blueprint
from flask_assets import Environment, Bundle
from flask_wtf.csrf import CsrfProtect


class MapleBootstrap(object):
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.assets = None
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        self.author_name = app.config.get('AUTHOR_NAME', 'honmaple')
        self.csrf(app)
        self.blueprint(app)
        self.assets(app)
        self.filters(app)

    def csrf(self, app):
        csrf = CsrfProtect()
        csrf.init_app(app)

    def blueprint(self, app):
        blueprint = Blueprint(
            'bootstrap',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=app.static_url_path + '/bootstrap')

        app.register_blueprint(blueprint)

    def assets(self, app):
        assets = Environment(app)
        bundles = {
            'home_js': Bundle('bootstrap/js/jquery.min.js',
                              'bootstrap/js/bootstrap.min.js',
                              'bootstrap/js/honmaple.js',
                              output='bootstrap/assets/home.js',
                              filters='jsmin'),
            'home_css': Bundle('bootstrap/css/bootstrap.min.css',
                               'bootstrap/css/honmaple.css',
                               output='bootstrap/assets/home.css',
                               filters='cssmin')
        }
        if self.assets is not None:
            bundles = bundles.update(self.assets)
            assets.register(bundles)
        else:
            assets.register(bundles)

    def add_assets(self, asserts=None):
        self.assets = asserts

    def filters(self, app):
        def show_footer(author=self.author_name):
            return author

        app.jinja_env.globals['show_footer'] = show_footer
