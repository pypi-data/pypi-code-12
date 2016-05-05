# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Rattail->Rattail Data Import
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import Session
from rattail.db.importing import ImportHandler, QueryProvider, models, normal
from rattail.util import OrderedDict


class RattailImportHandler(ImportHandler):
    """
    Import handler for data coming from a Rattail database.
    """

    def get_importers(self):
        importers = OrderedDict()
        importers['Message'] = MessageProvider
        importers['MessageRecipient'] = MessageRecipientProvider
        return importers

    def before_import(self):
        self.source_session = Session()

    def get_importer_kwargs(self, key):
        return {'source_session': self.source_session}

    def after_import(self):
        self.source_session.close()
        del self.source_session


class RattailProvider(QueryProvider):
    """
    Base class for Rattail data providers.
    """
    key = 'uuid'

    @property
    def normalize_progress_message(self):
        return "Reading {} data from Rattail".format(self.model_name)

    def setup(self):
        self.normalizer = self.normalizer_class()

    def query(self):
        return self.source_session.query(self.model_class)

    def normalize(self, instance):
        return self.normalizer.normalize(instance)


class MessageProvider(RattailProvider):
    """
    Import provider for Rattail message data.
    """
    importer_class = models.MessageImporter
    normalizer_class = normal.MessageNormalizer
    supported_fields = [
        'uuid',
        'sender_uuid',
        'subject',
        'body',
        'sent',
    ]


class MessageRecipientProvider(RattailProvider):
    """
    Import provider for Rattail message recipient data.
    """
    importer_class = models.MessageRecipientImporter
    normalizer_class = normal.MessageRecipientNormalizer
    supported_fields = [
        'uuid',
        'message_uuid',
        'recipient_uuid',
        'status',
    ]
