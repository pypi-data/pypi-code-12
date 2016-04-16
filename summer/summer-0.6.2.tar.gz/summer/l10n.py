# -*- coding: utf-8 -*-
# Time-stamp: < l10n.py (2016-02-14 02:38) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""Based on *Python*'s :py:mod:`gettext` module."""

import gettext
import logging

from .ex import SummerConfigurationException

logger = logging.getLogger(__name__)


class Localization(object):

    """Provides localization (l10n) services.  If properly configured in
    *summer* configuration file, it loads all the defined languages and
    installs :py:func:`gettext._` function into global namespace.

    """

    def __init__(self, domain: str, l10n_dir: str, languages: list):
        """Creates :py:class:`Localization` instance.

        Args:

            domain: gettext domain

            l10n_dir: directory path for gettext compiled data

            languages: list of supported languages
        """
        self.domain = domain
        self.l10n_dir = l10n_dir
        self.languages = languages
        try:
            self.lang = gettext.translation(self.domain,
                                            self.l10n_dir,
                                            self.languages)
            self.lang.install()
            logger.info("l10n installed with lang %s", self.lang)
        except Exception as ex:
            msg = "l10n not installed, check your settings, ex == %s" % (ex,)
            raise SummerConfigurationException(msg)
