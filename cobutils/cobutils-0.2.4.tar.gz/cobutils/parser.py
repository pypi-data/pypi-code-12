#!/usr/bin/python

from decimal import Decimal
import locale
import string
import math
import itertools
import struct

locale.setlocale(locale.LC_ALL, '')

IGNORE_PARSER_ERROR = True

class RecordParser(object):
    def __init__(self, filename=None, file=None, it=None):
        if filename:
            self.lines = open(filename)
        elif file:
            self.lines = file
        elif it:
            self.lines = it
        else:
           raise ValueError("No definition source provided")


    def tokenizer(self):
        # convert all to lower
        reg_file = (line.lower() for line in self.lines)
        # remove comments
        reg_file = filter(lambda x: x and x[6:7] != '*', reg_file)
        reg_file = filter(lambda x: x and x[0] != '*', reg_file)
        for line in reg_file:
            self.current_line = line
            for token in line.replace('\t',' ').split(' '):
                token = token.strip()
                if token == '':
                    continue
                if token.endswith('.'):
                    yield token[:-1]
                    yield token[-1]
                else:
                    yield token

    def __iter__(self):
        return self.parse_fields()

    def parse_fields(self):
        itoken = self.tokenizer()
        level = None
        for token in itoken:
            level, name, pic, occurs, redefines = 0, 'filler', None, 0, None
            # level
            level = int(token)
            # varname or pic
            token = next(itoken)
            if token == 'pic':
                name = 'filler'
            else:
                name = token
                token = next(itoken)

            while token != '.':
                # possible values . pic redefines
                if token.lower() == 'pic':
                    pic = []
                    token = next(itoken)
                    while token not in ('.', 'occurs', 'redefines'):
                        pic.append(token)
                        token = next(itoken)
                    continue

                if token == 'occurs':
                    token = next(itoken)
                    occurs = int(token)
                    token = next(itoken)
                    continue

                if token == 'redefines':
                    token = next(itoken)
                    redefines = token.replace("'", "")
                    token = next(itoken)
                    continue

                if token != '.':
                    raise Exception("Syntax Error <%s> <%s>" % \
                                           (token, self.current_line))

            yield level, name, pic, occurs, redefines


EDIT_CHARS = '+-/.,zb'
NUMERIC_CHARS = '0123456789vs()'

ZERO = Decimal(0)


class Picture(object):
    def __init__(self, pic):
        self.pic = pic
        self.size = 0
        self.is_edited = False
        self.is_text = False
        self.is_numeric = False
        self.is_signed = False
        self.int_digits = 0
        self.dec_digits = 0
        self.total_digits = 0
        self.comp = None
        self.sign_leading = False
        self.sign_trailing = False
        if pic:
            self.parse_picture(pic[:])

    def count_part(self, part):
        if '(' in part:
            if part[1] == '(' and part[-1] == ')':
                num = part[2:-1]
                return int(num)
            else:
                raise Exception("unsuported picture")
        else:
            return len(part)

    def parse_picture(self, pic):

        picture = pic[0]
        del(pic[0])

        if any(x in EDIT_CHARS for x in picture):
            self.is_edited = True
            self.size = len(picture)
            return

        if picture[0] == 'x':
            self.is_text = True
            self.size = self.count_part(picture)
            return

        self.is_numeric = True

        if any(x not in NUMERIC_CHARS for x in picture):
            raise Exception("Picture not suported <%s>" % picture)

        if picture[0] == 's':
            self.is_signed = True
            picture = picture[1:]

        ints, v, decs = picture.partition('v')
        self.int_digits = self.count_part(ints)
        self.dec_digits = self.count_part(decs)
        self.total_digits = self.int_digits + self.dec_digits
        self.size = self.total_digits

        if len(pic) > 0 and pic[0] == 'display':
            pic.pop(0)

        if len(pic) > 0 and pic[0].startswith('comp'):
            self.comp = pic[0]
            del(pic[0])
            if self.comp in ('comp-3', 'computational-3'):
                self.size = int(math.ceil(float(self.total_digits + 1) / 2))
            elif self.comp in ('comp', 'computational'):
                if self.total_digits >= 12:
                  self.size = 6
                else:
                  self.size = 4
            else:
                raise Exception("%s type not suported" % self.comp)

        if not pic:
            return

        if pic[0] == 'sign':
            if pic[1] == 'leading':
                self.size = self.size + 1
                self.sign_leading = True
            elif pic[1] == 'trailing':
                self.size = self.size + 1
                self.sign_trailing = True
            else:
                raise Exception("sign not suported")
            del(pic[0])
            del(pic[0])
            if pic[0] == 'separate':
                del(pic[0])

        return

    def extract_comp_3(self, reg):
        positions = []
        for c in reg.decode('latin1'):
            c1 = ord(c) & 0x0F
            c0 = (ord(c) & 0xF0) >> 4
            positions.append(c0)
            positions.append(c1)

        if not positions:
            return Decimal(0)
        # if even eliminate first position
        if (self.total_digits % 2) == 0:
            positions = positions[1:]

        if positions[-1] == 15:
            sign = 0
        else:
            sign = 1

        #hexvals = [hex(ord(c)) for c in reg]
        #print hexvals ,"->",positions,positions[:self.total_digits]
        if not filter(None, positions):
            sign = 0
        num = Decimal((sign, positions[:self.total_digits], -self.dec_digits))
        return num

    def extract_comp(self, reg):
        if self.total_digits >= 12:
           # 6 bytes unpack
           #unpacked1 = struct.unpack('>l', reg[2:])[0]
           x1, x2 = struct.unpack('>Hl', reg)
           unpacked = (x1 << 16) | x2
        else:
           unpacked = struct.unpack('>l', reg)[0]
        return Decimal(unpacked) / (10 ** self.dec_digits)

    def extract_display(self, reg):

        if not reg.strip(b'+- 0'):
            return ZERO
        reg = reg.decode('latin1')

        sign = 0
        if self.sign_leading:
            if reg[0] == '-':
                sign = 1
            reg = reg[1:]
        elif self.sign_trailing:
            if reg[-1] == '-':
                sign = 1
            reg = reg[:-1]
        else:
            c = reg[-1]
            if c not in ('0123456789'):
                #check sign
                if c == '{':
                    reg = reg[:-1] + "0"
                elif c == '}':
                    reg = reg[:-1] + "0"
                    sign = 1
                elif c in ('ABCDEFGHI'):
                    reg = reg[:-1] + "%d" % (ord(c) - ord('A') + 1)
                elif c in ('JKLMNOPQR'):
                    sign = 1
                    reg = reg[:-1] + "%d" % (ord(c) - ord('J') + 1)

        num = Decimal((sign, tuple(map(int, reg)), -self.dec_digits))
        return num

    def extract(self, reg):
        if self.is_text or self.is_edited:
            return reg

        if self.comp == 'comp-3':
            return self.extract_comp_3(reg)

        if self.comp == 'comp':
            return self.extract_comp(reg)

        return self.extract_display(reg)

    def get_bytes_comp(self, value):
        value = int(value * (10 ** self.dec_digits))
        raw = struct.pack('>l', value)
        return raw

    def get_bytes_comp_3(self, value):
        raw = b""
        digits = list(map(int, self.get_bytes_display(abs(value))))

        if (self.total_digits % 2) == 0:
            digits.insert(0, 0)

        if value == 0:
            # This is 12 for COBC
            digits.append(15)
        elif value < 0:
            digits.append(13)
        else:
            digits.append(15)

        for i in range(0, len(digits), 2):
            c1 = (digits[i] & 0x0F) << 4
            c0 = digits[i + 1] & 0x0F
            c = c1 | c0
            raw = raw + struct.pack("B", c)

        return raw

    def get_bytes_display(self, value):

        if self.dec_digits == 0:
            value = int(value)
        else:
            value = Decimal(str(locale.atof(str(value))))
            value = value * (10 ** self.dec_digits)

        fmt = "%%0%dd" % self.total_digits
        raw = fmt % abs(value)
        #if sign == 0 and value == 0:
        #   print value, sign

        raw = raw[:self.total_digits]

        if self.is_signed:
            sign = value < 0
            if self.sign_trailing:
                raw = raw + (sign and "-" or "+")
            elif self.sign_leading:
                raw = (sign and "-" or "+") + raw
            elif sign:
                raw = raw[:-1] + '}JKLMNOPQR'[int(raw[-1])]

        return raw.encode('latin1')

    def get_bytes(self, value):
        if self.is_text or self.is_edited:
           # return as is with padding
            return value.ljust(self.size)[:self.size]

        raw = b""

        if self.comp == 'comp-3':
            raw = raw + self.get_bytes_comp_3(value)
        elif self.comp == 'comp':
            raw = raw + self.get_bytes_comp(value)
        else:
            raw = raw + self.get_bytes_display(value)

        return raw

    def get_initialized(self):
        if self.is_text or self.is_edited:
            return " " * self.size
        # is numeric
        sign = 0
        raw = ""
        if self.is_signed and self.sign_leading:
            raw = sign and "-" or "+"

        if self.comp == 'comp-3':
            raw = raw + self.get_bytes_comp_3(0, sign)
        else:
            raw = raw + self.get_bytes_display(0)

        if self.is_signed and self.sign_trailing:
            raw = raw + (sign and "-" or "+")

        return raw.encode('latin1')

    def get_sql_type(self):
        if self.is_text or self.is_edited:
            #return "character(%d)" % self.size
            return "varchar(%d)" % self.size
        # is numeric
        #if self.dec_digits == 0:
        #    # can be integer o small int
        #    if self.total_digits < 5:
        #        return "smallint"
        #    if self.total_digits < 9:
        #        return "integer"

        return "numeric(%d,%d)" % (self.total_digits, self.dec_digits)

    def pprint(self):
        if self.pic:
            return ' '.join(self.pic)
        else:
            return ''


class FieldDef(object):
    def __init__(self, level, parent, name, pic, redefined=None):
        self.level = level
        self.parent = parent
        self.name = name.replace("'", "")
        if redefined:
            self.is_redefines = True
        else:
            self.is_redefines = False

        self.picture = Picture(pic)
        self.children = []
        self.children_map = {}
        self._size = 0
        self.redefined = redefined

    def add_child(self, child, occurs):
        if child.level <= self.level:
            raise Exception('level error')
        self.children.append((child, occurs))
        self.register_child(child.name, child)

    def register_child(self, name, child):
        self.children_map[name] = child
        if self.parent:
            self.parent.register_child(name, child)

    def pprint(self, indent=0):
        res = " %s %02d %s %s " %  \
            (" " * indent, self.level, self.name, self.picture.pprint())
        if self.is_redefines:
            res = res + " redefines " + self.redefined.name
        res = res + " ->%d\n" % self.size()
        for child, occurs in self.children:
            if occurs > 0:
                res = res + child.pprint(indent + 1) * occurs
            else:
                res = res + child.pprint(indent + 1)

        return res

    def del_redefines(self):
        for child, occurs in self.children:
            if child.is_redefines:
                self.children.remove((child, occurs))
            else:
                child.del_redefines()

    def size(self):
        if self._size == 0:
            if self.is_redefines or self.picture.size == 0:
                self._size = sum(child.size() * max(occurs, 1) \
                    for child, occurs in self.children \
                            if not child.is_redefines)
            else:
                self._size = self.picture.size
        return self._size

    def fieldname(self, idx=0, sql=False, levelidx=0):
        if idx == 0:
            idx = levelidx
        if idx > 0:
            if sql:
                sqlname = self.name.replace('-', '_')
                return "%s_%s" % (sqlname, idx)
            else:
                return "%s(%s)" % (self.name, idx)
        else:
            if sql:
                return self.name.replace('-', '_')
            else:
                return self.name

    def extract(self, reg, idx=0, levelidx=0, sql=False):
        res = {}
        position = 0
        size = 0
        if self.children:
            for child, occurs in self.children:
                if child.redefined:
                    if occurs > 0:
                        for i in range(1, occurs + 1):
                            data = reg[position:position + size]
                            res.update(child.extract(data, i, sql=sql))
                    else:
                            data = reg[position:position + size]
                            res.update(child.extract(data, levelidx=idx, sql=sql))
                else:
                    if occurs > 0:
                        for i in range(1, occurs + 1):
                            position = position + size
                            size = child.size()
                            data = reg[position:position + size]
                            res.update(child.extract(data, i, sql=sql))
                    else:
                            position = position + size
                            size = child.size()
                            data = reg[position:position + size]
                            res.update(child.extract(data, levelidx=idx, sql=sql))
        else:
            name = self.fieldname(idx, levelidx=levelidx, sql=sql)
            if IGNORE_PARSER_ERROR:
                try:
                    res[name] = self.picture.extract(reg)
                except ValueError:
                    # print "%s : <%s>" %(name,reg)
                    res[name] = Decimal(0)
            else:
                res[name] = self.picture.extract(reg)
        return res

    def get_bytes(self, values, idx=0, levelidx=0):
        raw = b""
        if self.children:
            for child, occurs in self.children:
                if child.redefined:
                    # take only first redefines
                    continue
                else:
                    if occurs > 0:
                        for i in range(1, occurs + 1):
                            raw = raw + \
                                child.get_bytes(values, i, levelidx=idx)
                    else:
                        raw = raw + child.get_bytes(values, levelidx=idx)
        else:
            name = self.fieldname(idx, levelidx=levelidx)
            if name in values:
                raw = raw + self.picture.get_bytes(values[name])
            else:
                # initialize value

                raw = raw + self.picture.get_initialized()
        return raw

    def get_sql_fields(self, idx=0, levelidx=0):
        res = []
        if self.children:
            for child, occurs in self.children:
                if child.redefined:
                    # take only first redefines
                    continue
                else:
                    if occurs > 0:
                        for i in range(1, occurs + 1):
                            res.extend(child.get_sql_fields(i, levelidx=idx))
                    else:
                        res.extend(child.get_sql_fields(levelidx=idx))
        else:
            fieldname = self.fieldname(idx, sql=True, levelidx=levelidx)
            #fieldname = fieldname.replace('(', '_').strip(')')
            res.append((fieldname, self.picture.get_sql_type()))
        return res

    def get_sql(self, idx=0, levelidx=0):
        if self.children:
            sql = []
            for child, occurs in self.children:
                if child.redefined:
                    # take only first redefines
                    continue
                else:
                    if occurs > 0:
                        for i in range(1, occurs + 1):
                            sql = sql + child.get_sql(i, idx)
                    else:
                        sql = sql + child.get_sql(levelidx=idx)
        else:
            name = self.fieldname(idx, sql=True, levelidx=levelidx)
            _type = self.picture.get_sql_type()
            sql = ["    %s %s" % (name, _type)]
        return sql

    def fieldnames(self, idx=0, sql=False, levelidx=0):
        res = []
        if self.children:
            for child, occurs in self.children:
                if occurs > 0:
                    for i in range(1, occurs + 1):
                        res.extend(child.fieldnames(i, sql, levelidx=idx))
                else:
                    res.extend(child.fieldnames(sql=sql, levelidx=idx))
        else:
            res.append(self.fieldname(idx, sql, levelidx=levelidx))
        return res


class RecordDef(FieldDef):
    def __init__(self, name):
        super(RecordDef, self).__init__(1, None, name, None)


def load_definition(filename=None, it=None):

    ifields = iter(RecordParser(filename=filename, it=it))
    level, name, pic, occurs, redefines = next(ifields)
    if level != 1:
        raise Exception("Syntax Error <level %s>" % level)
    if pic is not None:
        raise Exception("Syntax Error <pic %s>" % pic)

    reg = RecordDef(name)
    parent = reg
    for level, name, pic, occurs, redefines in ifields:
        while level <= parent.level:
            parent = parent.parent

        redefined = reg.children_map.get(redefines)
        current = FieldDef(level, parent, name, pic, redefined)
        parent.add_child(current, occurs)

        if pic == None:
            parent = current

    #reg.del_redefines()
    #print reg.pprint()

    return reg

def load_definition_from_text(text):
    return load_definition(it=text.split("\n"))

def load_definition_from_file(filename):
    return load_definition(filename=filename)
    
