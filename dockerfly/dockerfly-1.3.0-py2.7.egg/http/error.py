#!/bin/env python
# -*- coding: utf-8 -*-

errors = {
    '200': 'OK',             # GET success
    '201': 'CREATED',        # POST success
    '202': 'ACCEPTED',       # PUT success
    '400': 'BAD REQUEST',    # Wrong path or unsupported parameters
    '401': 'UNAUTHORIZED',   # Need Authorize
    '403': 'FORBIDDEN',      # forbidden to access
    '404': 'NOT FOUND',      # Resource not exists
    '500': 'INTERNAL ERROR'  # Server error
}
