"""
This module is imported on app ready (see __init__).
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . import models
from .tools import relations


@receiver((post_save, post_delete), sender=models.Link)
def lru_cache_clear(**kwargs): # pylint: disable=unused-argument
    "Clear the lru cache."
    to_clear = [relations.get_linked_ids, relations.get_nodes_recursive_from]

    for lru_chached in to_clear:
        lru_chached.cache_clear()
