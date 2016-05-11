"""
This module is imported on app ready (see __init__).
"""

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .tools import models, relation

@receiver(m2m_changed, sender=models.ALL['Association'].associations.through)
def validate_associations(**kwargs):
    "Validate associations."
    if kwargs['action'] != 'pre_add':
        return

    if kwargs['reverse']:
        return

    ids = kwargs['pk_set']
    stems = relation.get_stems_by_id(kwargs['instance'].organisation.id,
                                     recursive=True)

    existing = set()
    for row in relation.flatten(stems):
        for entry in row:
            existing.add(entry)

    for entry in ids:
        if entry in existing:
            text = "Circular associations error on adding '%s'."
            text = text % relation.get_name(entry)
            raise ValueError(text)
