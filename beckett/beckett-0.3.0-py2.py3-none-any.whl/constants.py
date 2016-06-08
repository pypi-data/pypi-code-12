# -*- coding: utf-8 -*-

from requests.status_codes import codes

DEFAULT_VALID_STATUS_CODES = (
    codes.ok,  # 200
    codes.created,  # 201
    codes.no_content,  # 204
)
