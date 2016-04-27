#!/usr/bin/python

import os
import subprocess
import tempfile

from cStringIO import StringIO


class GraphRasterizer(object):
    def __init__(self, graph):
        self.graph = graph

    def graph_as_str(self):
        s = StringIO()
        self.graph.render(s)
        return s.getvalue()

    def write_tempfile(self):
        fd, fname = tempfile.mkstemp(suffix='.svg')
        f = os.fdopen(fd, 'w')
        self.graph.render(f)
        f.close()
        self.fname = fname
        return fname

    def delete_tempfile(self):
        try:
            os.unlink(self.fname)
        except (AttributeError, OSError):
            pass

    def asPNG(self):
        tmpfile = self.write_tempfile()
        image = self.rasterize('image/png', tmpfile)
        self.delete_tempfile()
        return image

    def asJPEG(self):
        tmpfile = self.write_tempfile()
        image = self.rasterize('image/jpeg', tmpfile)
        self.delete_tempfile()
        return image


class BatikRastizer(GraphRasterizer):
    def rasterize(self, mimetype, infile):
        if mimetype == 'image/png':
            outtmpfile = infile + '.png'
        else:
            outtmpfile = infile + '.jpg'

        proc = subprocess.Popen(['/usr/bin/rasterizer', '-scriptSecurityOff', '-m', mimetype, infile], close_fds=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        try:
            f = open(outtmpfile, 'rb')
            image = f.read()
            f.close()
        except IOError:
            return stdout

        os.unlink(outtmpfile)
        return image


class RSVGRasterizer(GraphRasterizer):
    def rasterize(self, mimetype, infile):
        if mimetype == 'image/png':
            format = 'png'
        else:
            format = 'jpeg'

        outfd, outtmpfile = tempfile.mkstemp(suffix='.' + format)
        os.close(outfd)

        proc = subprocess.Popen(['/usr/bin/rsvg', '-f', format, infile, outtmpfile], close_fds=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        try:
            f = open(outtmpfile, 'rb')
            image = f.read()
            f.close()
        except IOError:
            return stdout

        os.unlink(outtmpfile)
        return image
