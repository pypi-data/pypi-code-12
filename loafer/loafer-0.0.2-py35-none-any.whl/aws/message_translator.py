# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

import json
import logging

from ..message_translator import StringMessageTranslator

logger = logging.getLogger(__name__)


class SQSMessageTranslator(StringMessageTranslator):

    def translate(self, message):
        try:
            body = message['Body']
        except (KeyError, TypeError):
            logger.error('Missing Body key in SQS message. It really came from SQS ?')
            return {'content': None}

        try:
            return {'content': json.loads(body)}
        except json.decoder.JSONDecodeError as exc:
            logger.exception(exc)
            return {'content': None}
