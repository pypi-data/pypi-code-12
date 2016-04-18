"""
  Matrix Market I/O in Python.
  See http://math.nist.gov/MatrixMarket/formats.html
  for information about the Matrix Market format.
"""
#
# Author: Pearu Peterson <pearu@cens.ioc.ee>
# Created: October, 2004
#
# References:
#  http://math.nist.gov/MatrixMarket/
#
from __future__ import division, print_function, absolute_import

import os
import sys

from numpy import (asarray, real, imag, conj, zeros, ndarray, concatenate,
                   ones, ascontiguousarray, vstack, savetxt, fromfile,
                   fromstring)
from numpy.compat import asbytes, asstr

from scipy._lib.six import string_types
from scipy.sparse import coo_matrix, isspmatrix

__all__ = ['mminfo', 'mmread', 'mmwrite', 'MMFile']


# -----------------------------------------------------------------------------
def mminfo(source):
    """
    Return size and storage parameters from Matrix Market file-like 'source'.

    Parameters
    ----------
    source : str or file-like
        Matrix Market filename (extension .mtx) or open file-like object

    Returns
    -------
    rows : int
        Number of matrix rows.
    cols : int
        Number of matrix columns.
    entries : int
        Number of non-zero entries of a sparse matrix
        or rows*cols for a dense matrix.
    format : str
        Either 'coordinate' or 'array'.
    field : str
        Either 'real', 'complex', 'pattern', or 'integer'.
    symmetry : str
        Either 'general', 'symmetric', 'skew-symmetric', or 'hermitian'.
    """
    return MMFile.info(source)

# -----------------------------------------------------------------------------


def mmread(source):
    """
    Reads the contents of a Matrix Market file-like 'source' into a matrix.

    Parameters
    ----------
    source : str or file-like
        Matrix Market filename (extensions .mtx, .mtz.gz)
        or open file-like object.

    Returns
    -------
    a : ndarray or coo_matrix
        Dense or sparse matrix depending on the matrix format in the
        Matrix Market file.
    """
    return MMFile().read(source)

# -----------------------------------------------------------------------------


def mmwrite(target, a, comment='', field=None, precision=None, symmetry=None):
    """
    Writes the sparse or dense array `a` to Matrix Market file-like `target`.

    Parameters
    ----------
    target : str or file-like
        Matrix Market filename (extension .mtx) or open file-like object.
    a : array like
        Sparse or dense 2D array.
    comment : str, optional
        Comments to be prepended to the Matrix Market file.
    field : None or str, optional
        Either 'real', 'complex', 'pattern', or 'integer'.
    precision : None or int, optional
        Number of digits to display for real or complex values.
    symmetry : None or str, optional
        Either 'general', 'symmetric', 'skew-symmetric', or 'hermitian'.
        If symmetry is None the symmetry type of 'a' is determined by its
        values.
    """
    MMFile().write(target, a, comment, field, precision, symmetry)


###############################################################################
class MMFile (object):
    __slots__ = ('_rows',
                 '_cols',
                 '_entries',
                 '_format',
                 '_field',
                 '_symmetry')

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    @property
    def entries(self):
        return self._entries

    @property
    def format(self):
        return self._format

    @property
    def field(self):
        return self._field

    @property
    def symmetry(self):
        return self._symmetry

    @property
    def has_symmetry(self):
        return self._symmetry in (self.SYMMETRY_SYMMETRIC,
                                  self.SYMMETRY_SKEW_SYMMETRIC,
                                  self.SYMMETRY_HERMITIAN)

    # format values
    FORMAT_COORDINATE = 'coordinate'
    FORMAT_ARRAY = 'array'
    FORMAT_VALUES = (FORMAT_COORDINATE, FORMAT_ARRAY)

    @classmethod
    def _validate_format(self, format):
        if format not in self.FORMAT_VALUES:
            raise ValueError('unknown format type %s, must be one of %s' %
                             (format, self.FORMAT_VALUES))

    # field values
    FIELD_INTEGER = 'integer'
    FIELD_REAL = 'real'
    FIELD_COMPLEX = 'complex'
    FIELD_PATTERN = 'pattern'
    FIELD_VALUES = (FIELD_INTEGER, FIELD_REAL, FIELD_COMPLEX, FIELD_PATTERN)

    @classmethod
    def _validate_field(self, field):
        if field not in self.FIELD_VALUES:
            raise ValueError('unknown field type %s, must be one of %s' %
                             (field, self.FIELD_VALUES))

    # symmetry values
    SYMMETRY_GENERAL = 'general'
    SYMMETRY_SYMMETRIC = 'symmetric'
    SYMMETRY_SKEW_SYMMETRIC = 'skew-symmetric'
    SYMMETRY_HERMITIAN = 'hermitian'
    SYMMETRY_VALUES = (SYMMETRY_GENERAL, SYMMETRY_SYMMETRIC,
                       SYMMETRY_SKEW_SYMMETRIC, SYMMETRY_HERMITIAN)

    @classmethod
    def _validate_symmetry(self, symmetry):
        if symmetry not in self.SYMMETRY_VALUES:
            raise ValueError('unknown symmetry type %s, must be one of %s' %
                             (symmetry, self.SYMMETRY_VALUES))

    DTYPES_BY_FIELD = {FIELD_INTEGER: 'i',
                       FIELD_REAL: 'd',
                       FIELD_COMPLEX: 'D',
                       FIELD_PATTERN: 'd'}

    # -------------------------------------------------------------------------
    @staticmethod
    def reader():
        pass

    # -------------------------------------------------------------------------
    @staticmethod
    def writer():
        pass

    # -------------------------------------------------------------------------
    @classmethod
    def info(self, source):
        """
        Return size, storage parameters from Matrix Market file-like 'source'.

        Parameters
        ----------
        source : str or file-like
            Matrix Market filename (extension .mtx) or open file-like object

        Returns
        -------
        rows : int
            Number of matrix rows.
        cols : int
            Number of matrix columns.
        entries : int
            Number of non-zero entries of a sparse matrix
            or rows*cols for a dense matrix.
        format : str
            Either 'coordinate' or 'array'.
        field : str
            Either 'real', 'complex', 'pattern', or 'integer'.
        symmetry : str
            Either 'general', 'symmetric', 'skew-symmetric', or 'hermitian'.
        """

        stream, close_it = self._open(source)

        try:

            # read and validate header line
            line = stream.readline()
            mmid, matrix, format, field, symmetry = \
                [asstr(part.strip()) for part in line.split()]
            if not mmid.startswith('%%MatrixMarket'):
                raise ValueError('source is not in Matrix Market format')
            if not matrix.lower() == 'matrix':
                raise ValueError("Problem reading file header: " + line)

            # http://math.nist.gov/MatrixMarket/formats.html
            if format.lower() == 'array':
                format = self.FORMAT_ARRAY
            elif format.lower() == 'coordinate':
                format = self.FORMAT_COORDINATE

            # skip comments
            while line.startswith(b'%'):
                line = stream.readline()

            line = line.split()
            if format == self.FORMAT_ARRAY:
                if not len(line) == 2:
                    raise ValueError("Header line not of length 2: " + line)
                rows, cols = map(int, line)
                entries = rows * cols
            else:
                if not len(line) == 3:
                    raise ValueError("Header line not of length 3: " + line)
                rows, cols, entries = map(int, line)

            return (rows, cols, entries, format, field.lower(),
                    symmetry.lower())

        finally:
            if close_it:
                stream.close()

    # -------------------------------------------------------------------------
    @staticmethod
    def _open(filespec, mode='rb'):
        """ Return an open file stream for reading based on source.

        If source is a file name, open it (after trying to find it with mtx and
        gzipped mtx extensions).  Otherwise, just return source.

        Parameters
        ----------
        filespec : str or file-like
            String giving file name or file-like object
        mode : str, optional
            Mode with which to open file, if `filespec` is a file name.

        Returns
        -------
        fobj : file-like
            Open file-like object.
        close_it : bool
            True if the calling function should close this file when done,
            false otherwise.
        """
        close_it = False
        if isinstance(filespec, string_types):
            close_it = True

            # open for reading
            if mode[0] == 'r':

                # determine filename plus extension
                if not os.path.isfile(filespec):
                    if os.path.isfile(filespec+'.mtx'):
                        filespec = filespec + '.mtx'
                    elif os.path.isfile(filespec+'.mtx.gz'):
                        filespec = filespec + '.mtx.gz'
                    elif os.path.isfile(filespec+'.mtx.bz2'):
                        filespec = filespec + '.mtx.bz2'
                # open filename
                if filespec.endswith('.gz'):
                    import gzip
                    stream = gzip.open(filespec, mode)
                elif filespec.endswith('.bz2'):
                    import bz2
                    stream = bz2.BZ2File(filespec, 'rb')
                else:
                    stream = open(filespec, mode)

            # open for writing
            else:
                if filespec[-4:] != '.mtx':
                    filespec = filespec + '.mtx'
                stream = open(filespec, mode)
        else:
            stream = filespec

        return stream, close_it

    # -------------------------------------------------------------------------
    @staticmethod
    def _get_symmetry(a):
        m, n = a.shape
        if m != n:
            return MMFile.SYMMETRY_GENERAL
        issymm = True
        isskew = True
        isherm = a.dtype.char in 'FD'

        # sparse input
        if isspmatrix(a):
            # check if number of nonzero entries of lower and upper triangle
            # matrix are equal
            a = a.tocoo()
            (row, col) = a.nonzero()
            if (row < col).sum() != (row > col).sum():
                return MMFile.SYMMETRY_GENERAL

            # define iterator over symmetric pair entries
            a = a.todok()

            def symm_iterator():
                for ((i, j), aij) in a.items():
                    if i > j:
                        aji = a[j, i]
                        yield (aij, aji)

        # non-sparse input
        else:
            # define iterator over symmetric pair entries
            def symm_iterator():
                for j in range(n):
                    for i in range(j+1, n):
                        aij, aji = a[i][j], a[j][i]
                        yield (aij, aji)

        # check for symmetry
        for (aij, aji) in symm_iterator():
            if issymm and aij != aji:
                issymm = False
            if isskew and aij != -aji:
                isskew = False
            if isherm and aij != conj(aji):
                isherm = False
            if not (issymm or isskew or isherm):
                break

        # return symmetry value
        if issymm:
            return MMFile.SYMMETRY_SYMMETRIC
        if isskew:
            return MMFile.SYMMETRY_SKEW_SYMMETRIC
        if isherm:
            return MMFile.SYMMETRY_HERMITIAN
        return MMFile.SYMMETRY_GENERAL

    # -------------------------------------------------------------------------
    @staticmethod
    def _field_template(field, precision):
        return {MMFile.FIELD_REAL: '%%.%ie\n' % precision,
                MMFile.FIELD_INTEGER: '%i\n',
                MMFile.FIELD_COMPLEX: '%%.%ie %%.%ie\n' %
                    (precision, precision)
                }.get(field, None)

    # -------------------------------------------------------------------------
    def __init__(self, **kwargs):
        self._init_attrs(**kwargs)

    # -------------------------------------------------------------------------
    def read(self, source):
        """
        Reads the contents of a Matrix Market file-like 'source' into a matrix.

        Parameters
        ----------
        source : str or file-like
            Matrix Market filename (extensions .mtx, .mtz.gz)
            or open file object.

        Returns
        -------
        a : ndarray or coo_matrix
            Dense or sparse matrix depending on the matrix format in the
            Matrix Market file.
        """
        stream, close_it = self._open(source)

        try:
            self._parse_header(stream)
            return self._parse_body(stream)

        finally:
            if close_it:
                stream.close()

    # -------------------------------------------------------------------------
    def write(self, target, a, comment='', field=None, precision=None,
              symmetry=None):
        """
        Writes sparse or dense array `a` to Matrix Market file-like `target`.

        Parameters
        ----------
        target : str or file-like
            Matrix Market filename (extension .mtx) or open file-like object.
        a : array like
            Sparse or dense 2D array.
        comment : str, optional
            Comments to be prepended to the Matrix Market file.
        field : None or str, optional
            Either 'real', 'complex', 'pattern', or 'integer'.
        precision : None or int, optional
            Number of digits to display for real or complex values.
        symmetry : None or str, optional
            Either 'general', 'symmetric', 'skew-symmetric', or 'hermitian'.
            If symmetry is None the symmetry type of 'a' is determined by its
            values.
        """

        stream, close_it = self._open(target, 'wb')

        try:
            self._write(stream, a, comment, field, precision, symmetry)

        finally:
            if close_it:
                stream.close()
            else:
                stream.flush()

    # -------------------------------------------------------------------------
    def _init_attrs(self, **kwargs):
        """
        Initialize each attributes with the corresponding keyword arg value
        or a default of None
        """

        attrs = self.__class__.__slots__
        public_attrs = [attr[1:] for attr in attrs]
        invalid_keys = set(kwargs.keys()) - set(public_attrs)

        if invalid_keys:
            raise ValueError('''found %s invalid keyword arguments, please only
                                use %s''' % (tuple(invalid_keys),
                                             public_attrs))

        for attr in attrs:
            setattr(self, attr, kwargs.get(attr[1:], None))

    # -------------------------------------------------------------------------
    def _parse_header(self, stream):
        rows, cols, entries, format, field, symmetry = \
            self.__class__.info(stream)
        self._init_attrs(rows=rows, cols=cols, entries=entries, format=format,
                         field=field, symmetry=symmetry)

    # -------------------------------------------------------------------------
    def _parse_body(self, stream):
        rows, cols, entries, format, field, symm = (self.rows, self.cols,
                                                    self.entries, self.format,
                                                    self.field, self.symmetry)

        try:
            from scipy.sparse import coo_matrix
        except ImportError:
            coo_matrix = None

        dtype = self.DTYPES_BY_FIELD.get(field, None)

        has_symmetry = self.has_symmetry
        is_complex = field == self.FIELD_COMPLEX
        is_skew = symm == self.SYMMETRY_SKEW_SYMMETRIC
        is_herm = symm == self.SYMMETRY_HERMITIAN
        is_pattern = field == self.FIELD_PATTERN

        if format == self.FORMAT_ARRAY:
            a = zeros((rows, cols), dtype=dtype)
            line = 1
            i, j = 0, 0
            while line:
                line = stream.readline()
                if not line or line.startswith(b'%'):
                    continue
                if is_complex:
                    aij = complex(*map(float, line.split()))
                else:
                    aij = float(line)
                a[i, j] = aij
                if has_symmetry and i != j:
                    if is_skew:
                        a[j, i] = -aij
                    elif is_herm:
                        a[j, i] = conj(aij)
                    else:
                        a[j, i] = aij
                if i < rows-1:
                    i = i + 1
                else:
                    j = j + 1
                    if not has_symmetry:
                        i = 0
                    else:
                        i = j
            if not (i in [0, j] and j == cols):
                raise ValueError("Parse error, did not read all lines.")

        elif format == self.FORMAT_COORDINATE and coo_matrix is None:
            # Read sparse matrix to dense when coo_matrix is not available.
            a = zeros((rows, cols), dtype=dtype)
            line = 1
            k = 0
            while line:
                line = stream.readline()
                if not line or line.startswith(b'%'):
                    continue
                l = line.split()
                i, j = map(int, l[:2])
                i, j = i-1, j-1
                if is_complex:
                    aij = complex(*map(float, l[2:]))
                else:
                    aij = float(l[2])
                a[i, j] = aij
                if has_symmetry and i != j:
                    if is_skew:
                        a[j, i] = -aij
                    elif is_herm:
                        a[j, i] = conj(aij)
                    else:
                        a[j, i] = aij
                k = k + 1
            if not k == entries:
                ValueError("Did not read all entries")

        elif format == self.FORMAT_COORDINATE:
            # Read sparse COOrdinate format

            if entries == 0:
                # empty matrix
                return coo_matrix((rows, cols), dtype=dtype)

            try:
                if not _is_fromfile_compatible(stream):
                    flat_data = fromstring(stream.read(), sep=' ')
                else:
                    # fromfile works for normal files
                    flat_data = fromfile(stream, sep=' ')
            except Exception:
                # fallback - fromfile fails for some file-like objects
                flat_data = fromstring(stream.read(), sep=' ')

                # TODO use iterator (e.g. xreadlines) to avoid reading
                # the whole file into memory

            if is_pattern:
                flat_data = flat_data.reshape(-1, 2)
                I = ascontiguousarray(flat_data[:, 0], dtype='intc')
                J = ascontiguousarray(flat_data[:, 1], dtype='intc')
                V = ones(len(I), dtype='int8')  # filler
            elif is_complex:
                flat_data = flat_data.reshape(-1, 4)
                I = ascontiguousarray(flat_data[:, 0], dtype='intc')
                J = ascontiguousarray(flat_data[:, 1], dtype='intc')
                V = ascontiguousarray(flat_data[:, 2], dtype='complex')
                V.imag = flat_data[:, 3]
            else:
                flat_data = flat_data.reshape(-1, 3)
                I = ascontiguousarray(flat_data[:, 0], dtype='intc')
                J = ascontiguousarray(flat_data[:, 1], dtype='intc')
                V = ascontiguousarray(flat_data[:, 2], dtype='float')

            I -= 1  # adjust indices (base 1 -> base 0)
            J -= 1

            if has_symmetry:
                mask = (I != J)       # off diagonal mask
                od_I = I[mask]
                od_J = J[mask]
                od_V = V[mask]

                I = concatenate((I, od_J))
                J = concatenate((J, od_I))

                if is_skew:
                    od_V *= -1
                elif is_herm:
                    od_V = od_V.conjugate()

                V = concatenate((V, od_V))

            a = coo_matrix((V, (I, J)), shape=(rows, cols), dtype=dtype)
        else:
            raise NotImplementedError(format)

        return a

    #  ------------------------------------------------------------------------
    def _write(self, stream, a, comment='', field=None, precision=None,
               symmetry=None):

        if isinstance(a, list) or isinstance(a, ndarray) or \
           isinstance(a, tuple) or hasattr(a, '__array__'):
            rep = self.FORMAT_ARRAY
            a = asarray(a)
            if len(a.shape) != 2:
                raise ValueError('Expected 2 dimensional array')
            rows, cols = a.shape

            if field is not None:

                if field == self.FIELD_INTEGER:
                    a = a.astype('i')
                elif field == self.FIELD_REAL:
                    if a.dtype.char not in 'fd':
                        a = a.astype('d')
                elif field == self.FIELD_COMPLEX:
                    if a.dtype.char not in 'FD':
                        a = a.astype('D')

        else:
            if not isspmatrix(a):
                raise ValueError('unknown matrix type: %s' % type(a))
            rep = 'coordinate'
            rows, cols = a.shape

        typecode = a.dtype.char

        if precision is None:
            if typecode in 'fF':
                precision = 8
            else:
                precision = 16

        if field is None:
            kind = a.dtype.kind
            if kind == 'i':
                field = 'integer'
            elif kind == 'f':
                field = 'real'
            elif kind == 'c':
                field = 'complex'
            else:
                raise TypeError('unexpected dtype kind ' + kind)

        if symmetry is None:
            symmetry = self._get_symmetry(a)

        # validate rep, field, and symmetry
        self.__class__._validate_format(rep)
        self.__class__._validate_field(field)
        self.__class__._validate_symmetry(symmetry)

        # write initial header line
        stream.write(asbytes('%%MatrixMarket matrix {0} {1} {2}\n'.format(rep,
            field, symmetry)))

        # write comments
        for line in comment.split('\n'):
            stream.write(asbytes('%%%s\n' % (line)))

        template = self._field_template(field, precision)

        # write dense format
        if rep == self.FORMAT_ARRAY:

            # write shape spec
            stream.write(asbytes('%i %i\n' % (rows, cols)))

            if field in (self.FIELD_INTEGER, self.FIELD_REAL):

                if symmetry == self.SYMMETRY_GENERAL:
                    for j in range(cols):
                        for i in range(rows):
                            stream.write(asbytes(template % a[i, j]))
                else:
                    for j in range(cols):
                        for i in range(j, rows):
                            stream.write(asbytes(template % a[i, j]))

            elif field == self.FIELD_COMPLEX:

                if symmetry == self.SYMMETRY_GENERAL:
                    for j in range(cols):
                        for i in range(rows):
                            aij = a[i, j]
                            stream.write(asbytes(template % (real(aij),
                                                             imag(aij))))
                else:
                    for j in range(cols):
                        for i in range(j, rows):
                            aij = a[i, j]
                            stream.write(asbytes(template % (real(aij),
                                                             imag(aij))))

            elif field == self.FIELD_PATTERN:
                raise ValueError('pattern type inconsisted with dense format')

            else:
                raise TypeError('Unknown field type %s' % field)

        # write sparse format
        else:

            coo = a.tocoo()  # convert to COOrdinate format

            # if symmetry format used, remove values above main diagonal
            if symmetry != self.SYMMETRY_GENERAL:
                lower_triangle_mask = coo.row >= coo.col
                coo = coo_matrix((coo.data[lower_triangle_mask],
                                 (coo.row[lower_triangle_mask],
                                  coo.col[lower_triangle_mask])),
                                 shape=coo.shape)

            # write shape spec
            stream.write(asbytes('%i %i %i\n' % (rows, cols, coo.nnz)))

            # make indices and data array
            if field == self.FIELD_PATTERN:
                IJV = vstack((coo.row, coo.col)).T
            elif field in [self.FIELD_INTEGER, self.FIELD_REAL]:
                IJV = vstack((coo.row, coo.col, coo.data)).T
            elif field == self.FIELD_COMPLEX:
                IJV = vstack((coo.row, coo.col, coo.data.real,
                              coo.data.imag)).T
            else:
                raise TypeError('Unknown field type %s' % field)
            IJV[:, :2] += 1  # change base 0 -> base 1

            # formats for row indices, col indices and data columns
            fmt = ('%i', '%i') + ('%%.%dg' % precision,) * (IJV.shape[1]-2)
            # save to file
            savetxt(stream, IJV, fmt=fmt)


def _is_fromfile_compatible(stream):
    """
    Check whether `stream` is compatible with numpy.fromfile.

    Passing a gzipped file object to ``fromfile/fromstring`` doesn't work with
    Python3.
    """
    if sys.version_info[0] < 3:
        return True

    bad_cls = []
    try:
        import gzip
        bad_cls.append(gzip.GzipFile)
    except ImportError:
        pass
    try:
        import bz2
        bad_cls.append(bz2.BZ2File)
    except ImportError:
        pass

    bad_cls = tuple(bad_cls)
    return not isinstance(stream, bad_cls)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import time
    for filename in sys.argv[1:]:
        print('Reading', filename, '...', end=' ')
        sys.stdout.flush()
        t = time.time()
        mmread(filename)
        print('took %s seconds' % (time.time() - t))
