import gzip


class gzopen(object):

    def __init__(self, fname):

        f = open(fname)
        if fname.endswith('.gz'):
            self.f = gzip.GzipFile(fileobj=f)
        else:
            self.f = f

    # Define '__enter__' and '__exit__' to use in
    # 'with' blocks. Always close the file and the
    # GzipFile if applicable.
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        try:
            self.f.fileobj.close()
        except AttributeError:
            pass
        finally:
            self.f.close()

    # Reproduce the interface of an open file
    # by encapsulation.
    def __getattr__(self, name):
        return getattr(self.f, name)

    def __iter__(self):
        return iter(self.f)

    def next(self):
        return next(self.f)
