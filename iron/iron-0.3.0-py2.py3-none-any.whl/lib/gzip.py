from gzip import GzipFile
from io import BytesIO

from ..core import Task


class gzip(Task):
    def lazy_gzip(self, input_stream):
        gzip_buffer = BytesIO()
        gzip_file = GzipFile(mode='wb', fileobj=gzip_buffer)
        try:
            for chunk in input_stream:
                gzip_file.write(chunk)
            gzip_file.flush()
        finally:
            gzip_file.close()
        yield gzip_buffer.getvalue()

    def process(self, inputs):
        for t, c, m in inputs:
            t2 = t.with_name(t.name + '.gz')
            yield t2, self.lazy_gzip(c), m
