#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_gulp
----------------------------------
http://pythontesting.net/framework/pytest/pytest-introduction/
Tests for `gulp` module.
"""

import gulp
import logging
import time


def setup_module(module):
    logging.basicConfig(level=60)


@gulp.time_this('{:5.3f} msec')
def test_time_profile():
    time.sleep(0.1)
    pass


def test_debug_level_0():
    lo = logging.getLogger('log_name')
    lo.debug('debug')
    lo.info('info')
    lo.warning('warning')
    lo.error('error')
    lo.critical('critical')


@gulp.debug_log(10, logger_name='log_name')
def test_debug_level_1():
    lo = logging.getLogger('log_name')
    time.sleep(0.1)
    lo.debug('x')
    lo.info('x')
    lo.warning('x')
    lo.error('x')
    lo.critical('x')
    time.sleep(0.1)


def test_debug_level_2():
    lo = logging.getLogger('log_name')
    time.sleep(0.1)
    lo.debug('debug')
    lo.info('info')
    lo.warning('warning')
    lo.error('error')
    lo.critical('critical')
    time.sleep(0.1)


@gulp.peek_vars()
def test_vars():
    return 'ok mod var'


class TestGulp:

    def setup(self):
        self.log = logging.getLogger('log_name')

    def teardown(self):
        pass

    @gulp.time_this('{:5.3f} msec')
    def test_class_time_profile(self):
        time.sleep(0.1)
        pass

    def test_class_debug_level_0(self):
        time.sleep(0.1)
        self.log.debug('debug')
        self.log.info('info')
        self.log.warning('warning')
        self.log.error('error')
        self.log.critical('critical')
        time.sleep(0.1)

    @gulp.debug_log(10, logger_name='log_name')
    def test_class_debug_level_1(self):
        time.sleep(0.1)
        self.log.debug('y')
        self.log.info('y')
        self.log.warning('y')
        self.log.error('y')
        self.log.critical('y')
        time.sleep(0.1)

    def test_class_debug_level_2(self):
        time.sleep(0.1)
        self.log.debug('debug')
        self.log.info('info')
        self.log.warning('warning')
        self.log.error('error')
        self.log.critical('critical')
        time.sleep(0.1)

    @gulp.peek_vars()
    def test_class_vars(self):
        return 'ok class var'
