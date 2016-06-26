from __future__ import unicode_literals

from django.template.loader import render_to_string
from . import models


def get_action_text(action):
    """
    Get a text respresentation of the Action
    :param action: Model, Action model instance
    :returns: String, text description of an Activity Action
    """
    context = {
        'actor': action.actor,
        'verb': action.verb,
        'action': action.action,
        'target': action.target,
        'timestamp': action.time_ago
    }

    if action.target:
        return (
            '{actor} {verb} {action} to {target} {timestamp}'
        ).format(**context)

    if action.action:
        return ('{actor} {verb} {action} {timestamp}').format(**context)

    return '{actor} {verb} {timestamp}'.format(**context)


def get_action_html(action):
    """
    Get a html respresentation of the Action
    :param action: Model, Action model instance
    :returns: String, html description of an Activity Action
    """
    return render_to_string('action.html', {'action': action})


def add_action(actor, verb, action=None, target=None):
    kwargs = {
        'actor': actor,
        'verb': verb,
        'action': action,
        'target': target,
    }
    # remove any None key values
    kwargs = {k: v for k, v in kwargs.items() if v}

    return models.Action.objects.create(**kwargs)
