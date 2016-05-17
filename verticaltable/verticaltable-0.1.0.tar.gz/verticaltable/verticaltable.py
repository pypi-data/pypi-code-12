import re
from collections import OrderedDict


def load(read_fp):
    return loads(read_fp.read())


re_comment = re.compile('^#.*\n', flags=re.MULTILINE)

re_row_separator = re.compile('^----+$', flags=re.MULTILINE)

re_item_separator = re.compile('^\[', flags=re.MULTILINE)
re_key_value = re.compile('^(\w+)\](.*)$', flags=re.DOTALL)


def get_parsed(source_text):
    for m in re_row_separator.split(source_text):
        d = OrderedDict()
        for kv in re_item_separator.split(m):
            m = re_key_value.match(kv)
            if m:
                key = m.group(1)
                value = m.group(2).strip()
                if key in d:
                    yield d
                    d = OrderedDict()
                d[key] = value
        if d:
            yield d


def loads(source_text):
    source_text = re_comment.sub('', source_text)

    return list(get_parsed(source_text))
