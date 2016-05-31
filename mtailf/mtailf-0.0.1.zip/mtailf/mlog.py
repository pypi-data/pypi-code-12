#!/usr/bin/env python
# -*- coding:utf-8 -*-

DEBUG = "\x1B[1;32m "
FAIL = "\x1B[1;31m "
ENDC = "\x1B[0m"


def debug(message):
    print DEBUG + message + ENDC


def debug_inline(message):
    print DEBUG + message + ENDC,


def info(message):
    print message

def info_inline(message):
    print message,


def error(message):
    print FAIL + message + ENDC

def error_inline(message):
    print FAIL + message + ENDC,
