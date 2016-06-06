###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################
import io
import concurrent.futures
from contextlib import ContextDecorator
from gzip import GzipFile
from queue import Queue, Empty


class QueueWriter(ContextDecorator):
    def __init__(self, queue: Queue):
        self.queue = queue

    def write(self, b):
        if b:
            self.queue.put(b)


class CompressingQueueWriter():
    def __init__(self, queue: Queue, compress_level=3):
        self.queue = queue
        self.writer = QueueWriter(queue)
        self.gzip = GzipFile(mode='wb', compresslevel=compress_level, fileobj=self.writer)

    def write(self, b):
        self.gzip.write(b)


class Exporter(object):
    """
    Exporters take a table and turn it into some other format. Subclasses only need to implement
    Exporter.dump(): all other methods are relying on this one. Subsequently, this abstract class
    doesn't implement it.
    """
    extension = None
    content_type = None
    compressable = True

    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        """Write contents of a exportable to file like object. The only method the file like object
        needs to support is write, which should take bytes.

        @param fo: file like object
        @param filename_hint: some formats (such as zipped) need a filename
        @param encoding_hint: encoding for bytes resulting bytes. Doesn't do anything for binary
                              formats such as ODS, XLSX or SPSS.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def dumps(self, table, filename_hint=None, encoding_hint="utf-8") -> bytes:
        """Export exportable and return value as bytes.

        @param filename_hint: some formats (such as zipped) need a filename
        @param encoding_hint: encoding for bytes resulting bytes. Doesn't do anything for binary
                              formats such as ODS, XLSX or SPSS.
        """
        fo = io.BytesIO()
        self.dump(table, fo, filename_hint=filename_hint, encoding_hint=encoding_hint)
        return fo.getvalue()

    def _dump_iter(self, queue: Queue, table, writer=None, filename_hint=None, encoding_hint="utf-8"):
        self.dump(table, (writer or QueueWriter)(queue), filename_hint=filename_hint, encoding_hint=encoding_hint)

    def dump_iter(self, table, buffer_size=20, filename_hint=None, writer=None, encoding_hint="utf-8") -> [bytes]:
        """Export exportable and return an iterator of bytes. This is particularly useful for Django,
        which supports streaming responses through iterators.

        @param buffer_size: store up to N write() message in buffer
        @param filename_hint: some formats (such as zipped) need a filename
        @param encoding_hint: encoding for bytes resulting bytes. Doesn't do anything for binary
                              formats such as ODS, XLSX or SPSS.
        """
        queue = Queue(maxsize=buffer_size)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._dump_iter, queue, table, writer, filename_hint, encoding_hint)

            while future.running() or not queue.empty():
                try:
                    # Make sure to quit if the thread threw an error
                    yield queue.get(timeout=0.2)
                except Empty:
                    continue

            # If any exceptions occurred while running _dump_iter, the exception will be thrown
            future.result()

    def dump_http_reponse(self, table, filename=None, compress=True, compress_level=3, encoding_hint="utf-8"):
        """Render exportable as a Django response.

        @param filename: filename to suggest to browser
        @param filename_hint: some formats (such as zipped) need a filename
        @param encoding_hint: encoding for bytes resulting bytes. Doesn't do anything for binary
                              formats such as ODS, XLSX or SPSS.
        @return: Django streaming HTTP response
        """
        # Inline import: not all users of table necessarily use Django
        from django.http.response import StreamingHttpResponse

        if compress and self.compressable:
            # Pass CompressQueueWriter to enable compression
            writer = lambda queue: CompressingQueueWriter(queue, compress_level=compress_level)
            content = self.dump_iter(table, encoding_hint=encoding_hint, filename_hint=filename, writer=writer)
            response = StreamingHttpResponse(content, content_type=self.content_type)
            response['Content-Encoding'] = "gzip"
        else:
            # Write without compression
            content = self.dump_iter(table, encoding_hint=encoding_hint, filename_hint=filename)
            response = StreamingHttpResponse(content, content_type=self.content_type)

        # Set attachment header to have a nice filename when downloading
        if filename:
            attachment = 'attachment; filename="{}.{}"'.format(filename, self.extension)
            response['Content-Disposition'] = attachment

        return response
