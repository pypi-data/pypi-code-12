# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import os.path


def validate_in(key, mapping):
    if key not in mapping:
        raise AssertionError("The key '%s' was not found in the mapping %s!" % (key, mapping))


def validate_response_is_ok(response, allowable_response_status_codes=frozenset([200])):
    if isinstance(allowable_response_status_codes, int):
        allowable_response_status_codes = {allowable_response_status_codes}
    if response.status_code not in allowable_response_status_codes:
        raise AssertionError(
            """response.status_code(%s) not in allowable_response_status_codes(%s) for the url\
             '%s' (request method:'%s'). response.content:\n%s""" % (
                response.status_code, allowable_response_status_codes,
                response.url,
                response.request.method,
                response.text[:1000]))


def validate_equal_case_insensitive(expected, actual, msg=None):
    if isinstance(expected, str) and isinstance(actual, str):
        if expected.lower() == expected.lower():
            # the arguments are strings and they are the same when ignoring case.
            return
    if msg:
        raise AssertionError("""actual(%s) != expected(%s)! %s""" % (actual, expected, msg))
    else:
        raise AssertionError("""actual(%s) != expected(%s)""" % (actual, expected))


def get_version():
    with open(os.path.join(os.path.dirname(__file__), 'VERSION.txt')) as version_file:
        return version_file.read().strip()
