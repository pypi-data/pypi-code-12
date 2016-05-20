from pathlib import Path


def lazy_read(p):
    p = Path(p)
    with p.open('rb') as f:
        while True:
            chunk = f.read(4096)
            if chunk == b'':
                break
            yield chunk


def write_to_file(dest, input_stream):
    with Path(dest).open('wb') as f:
        for chunk in input_stream:
            if not isinstance(chunk, bytes):
                raise TypeError('bytes expected in input stream, got {}:'.format(type(chunk)))
            f.write(chunk)
