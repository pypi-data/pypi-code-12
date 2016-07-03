# coding: utf-8

# Asynchronous Music Player Daemon client library for Python

# Copyright (C) 2015 Itaï BEN YAACOV

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from . import errors


class Parser(object):
    WELCOME_PREFIX = 'OK MPD '
    SUCCESS = 'OK'
    ERROR_PREFIX = 'ACK'

    def process_line(self, line):
        if line.startswith(self.ERROR_PREFIX):
            return errors.ReplyError(line)
        else:
            return self._parse_line(line)


class ParserWelcome(Parser):
    def _parse_line(self, line):
        if line.startswith(self.WELCOME_PREFIX):
            return line[len(self.WELCOME_PREFIX):]
        else:
            raise errors.ProtocolError(line)


class ParserCommandList(Parser):
    LIST_SUCCESS = 'list_OK'

    def __init__(self, parsers):
        self.reply = []
        self.parsers = list(parsers)
        for parser in self.parsers:
            parser.SUCCESS = self.LIST_SUCCESS
        self.current = 0

    def process_line(self, line):
        if self.current == len(self.parsers):
            if line == self.SUCCESS:
                return self.reply
            raise errors.ProtocolError(line)
        reply = self.parsers[self.current].process_line(line)
        if isinstance(reply, errors.ReplyError):
            return reply
        if reply is not None:
            self.reply.append(reply)
            self.current += 1


class ParserRaw(Parser):
    def __init__(self):
        self.reply = []

    def get_reply(self):
        return self.reply

    def _parse_line(self, line):
        if line == self.SUCCESS:
            return self.get_reply()
        delim = line.find(': ')
        if delim == -1:
            raise errors.ProtocolError(line)
        self.reply.append((line[:delim].lower(), line[delim + 2:]))


class ParserOK(ParserRaw):
    def get_reply(self):
        if self.reply == []:
            return True
        else:
            raise errors.ProtocolError(self.reply)


class ParserDict(ParserRaw):
    def get_reply(self):
        return dict(self.reply)


class ParserDicts(ParserRaw):
    new_items = ['file', 'directory', 'playlist']

    def get_reply(self):
        items = {}
        for field, value in self.reply:
            if field in self.new_items:
                item = {}
                items.setdefault(field, []).append(item)
            item[field] = value
        return items


class _ParserFieldDict(ParserRaw):
    def __init__(self, field):
        super(_ParserFieldDict, self).__init__()
        self.field = field

    def get_reply(self):
        items = []
        for field, value in super(_ParserFieldDict, self).get_reply():
            if field == self.field:
                item = {}
                items.append(item)
            item[field] = value
        return items


def ParserFieldDict(field):
    return lambda: _ParserFieldDict(field)


class ParserList(ParserRaw):
    def get_reply(self):
        return [value for field, value in self.reply]


class ParserLists(ParserRaw):
    def get_reply(self):
        lists = {}
        for field, value in self.reply:
            lists.setdefault(field, []).append(value)
        return lists


class ParserItem(ParserRaw):
    def get_reply(self):
        reply = super(ParserItem, self).get_reply()
        if len(reply) == 1:
            return reply[0][1]
        else:
            raise errors.ProtocolError(reply)


class _ParserSticker(ParserRaw):
    def get_reply(self):
        return [(field, value.split('=', 1)[1]) if field == 'sticker' else (field, value) for field, value in super(_ParserSticker, self).get_reply()]


class ParserStickerDict(_ParserFieldDict, _ParserSticker):
    def __init__(self):
        _ParserFieldDict.__init__(self, 'file')

    def get_reply(self):
        return {entry['file']: entry['sticker'] for entry in super(ParserStickerDict, self).get_reply()}


class ParserStickerItem(ParserItem, _ParserSticker):
    pass


class ParserStickerList(ParserRaw):
    def get_reply(self):
        return dict(value.split('=', 1) for field, value in super(ParserStickerList, self).get_reply())


class DeprecatedParser(Parser):
    def __init__(self, parser):
        self.parser = parser

    def process_line(self, line):
        reply = self.parser.process_line(line)
        if reply:
            return reply if isinstance(reply, errors.ReplyError) else DeprecationWarning(reply)


def deprecate(parser_class):
    return lambda: DeprecatedParser(parser_class())
