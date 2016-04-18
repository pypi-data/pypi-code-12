# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4


class IntMessageTranslator(object):

    def translate(self, message):
        try:
            number = int(message)
        except ValueError:
            return None
        return {'content': number}
