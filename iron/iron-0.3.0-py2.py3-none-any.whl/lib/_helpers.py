def as_text(c):
    if isinstance(c, str):
        return c
    else:
        return b''.join(c).decode('utf-8')


def as_byte_stream(s):
    if not isinstance(s, str):
        raise TypeError('Expected a string, got {}'.format(s))
    yield s.encode('utf-8')
