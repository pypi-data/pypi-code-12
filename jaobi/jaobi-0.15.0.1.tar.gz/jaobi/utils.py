# -*- coding: utf-8 -*-

import logging
import re


def generate_collection_scores(collection_dict, total_hits):
    """
    Generate a ordered list scored by percetage related to ``total_hits``
    """
    scores = []
    if total_hits == 0:
        return scores

    for item, hits in collection_dict.items():
        item_score = (100 * hits) / total_hits
        scores.append((item_score, item))
    return sorted(scores, reverse=True)


def sanitize_string(dirty_string):
    """ Removes html and replace odd quotation marks by ``"``.
    """
    forbidden = re.compile('<[script|SCRIPT|style|STYLE].*?>.*?<\/.*?>')
    tags = re.compile('<.*?>')
    quotations = re.compile('[“|”]')

    sanitized = re.sub(forbidden, '', dirty_string)
    sanitized = re.sub(tags, '', sanitized)
    sanitized = re.sub(quotations, '"', sanitized)

    return sanitized


def log(msg, level='info'):
    logger = logging.getLogger('jaobi')
    log = getattr(logger, level)
    log(msg)
