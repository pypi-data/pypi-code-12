"""Module with blocked matrix class"""


class matrix(object):
    """Blocked matrix class"""
    def __init__(self, nrow, ncol):
        """Initialize blocked matrix instance

        nrow: integer tuple, blocked row dimension
        ncol: integer tuple, blocked column dimension
        """
        from . import full
        self.rowblocks = len(nrow)
        self.colblocks = len(ncol)
        self.nrow = nrow
        self.ncol = ncol
        self.subblock = []
        self.irow = []
        self.icol = []
        for i in range(self.rowblocks):
            self.subblock.append([])
            self.irow.append(sum(self.nrow[:i]))
            self.icol.append(sum(self.ncol[:i]))
            for j in range(self.colblocks):
                self.subblock[i].append([])
                self.subblock[i][j] = full.matrix((nrow[i], ncol[j]))

    def __str__(self):
        """String representation of blocked matrix"""

        retstr = ""
        for i in range(self.rowblocks):
            for j in range(self.colblocks):
                retstr += "\nBlock (%d,%d)\n" % (i+1, j+1) + \
                    str(self.subblock[i][j])
        return retstr

    def T(self):
        """Transpose of blocked matrix"""

        new = matrix(self.ncol, self.nrow)
        for i in range(self.rowblocks):
            for j in range(self.colblocks):
                new.subblock[i][j] = self.subblock[j][i].transpose()
        return new

    def __mul__(self, other):
        """Multiplication of blocked matrices"""

        new = matrix(self.nrow, other.ncol)
        for i in range(self.rowblocks):
            for j in range(other.colblocks):
                if self.nrow[i]*other.ncol[j]:
                    for k in range(self.colblocks):
                        new.subblock[i][j] = \
                            self.subblock[i][k] * other.subblock[k][j]
        return new

    def random(self):
        """Fill matrix with random numbers"""
        for i in range(self.rowblocks):
            for j in range(self.colblocks):
                self.subblock[i][j].random()

    def unblock(self):
        """Unblock to full matrix"""

        from . import full
        nrows = sum(self.nrow)
        ncols = sum(self.ncol)
        new = full.matrix((nrows, ncols))
        for i in range(self.rowblocks):
            for j in range(self.colblocks):
                new[
                    self.irow[i]: self.irow[i] + self.nrow[i],
                    self.icol[j]: self.icol[j] + self.ncol[j]
                    ] = self.subblock[i][j]
        return new

if __name__ == "__main__": #pragma: no cover
    pass
