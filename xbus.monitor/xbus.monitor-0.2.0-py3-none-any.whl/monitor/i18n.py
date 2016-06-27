"""Internationalization helpers."""

from pyramid.i18n import (
    get_localizer,
    TranslationStringFactory,
)

translation_factory = None


def init_i18n(config):
    global translation_factory
    translation_factory = TranslationStringFactory('xbus_monitor')

    config.add_translation_dirs(
        'xbus.monitor:locale/'
    )


def req_l10n(request):
    global translation_factory
    localizer = get_localizer(request)
    return lambda string: localizer.translate(translation_factory(string))
