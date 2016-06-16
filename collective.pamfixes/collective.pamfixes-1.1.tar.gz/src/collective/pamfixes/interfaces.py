# -*- coding: utf-8 -*-
"""collective.pamfixes interfaces."""

# python imports
from pkg_resources import (
    get_distribution,
    parse_version,
)


pam_distribution = get_distribution('plone.app.multilingual')
pam_version = pam_distribution.version

# version-dependent import
if parse_version(pam_version) < parse_version('2.0'):
    from plone.multilingual.interfaces import (
        ITranslatable,
        ITranslationManager,
    )
else:
    from plone.app.multilingual.interfaces import (
        ITranslatable,
        ITranslationManager,
    )

assert(ITranslatable)
assert(ITranslationManager)
