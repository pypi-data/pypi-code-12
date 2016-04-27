import math
import re
import os
import cStringIO

class Table(object):
    class Value(object):
        def __init__(self, table, col, row, val):
            self.table=table        #reference to the parent table
            self.row=row            #row index in the parent table
            self.col=col            #column index in the parent table
            self.value=float(val)           #value
            self.displayvalue=str(int(self.value+0.5))
            self.frac=None

        #instead of all these weird and wonderful functions,
        # allow the table to be renomalized by the consumer and just provide two casts
        # cast to string: the value to be displayed - may contain units etc
        # cast to float fracOfMax(): a fraction in [0,1]
        def __str__(self):
            return self.displayvalue

        def __float__(self):
            if not self.table.normalized:
                self.table.normalize()
            return self.frac

#               def fracOfRow(self):
#                       """Turns out we still need this one"""
#                       self.__normalize()
#                       try:
#                               return float(self.value)/self.table.rowtotals[self.row]
#                       except ZeroDivisionError:
#                               return 0
#
#               def percentOfRow(self):
#                       return int(self.fracOfRow()*100+0.5)
#
#               def fracOfTotal(self):
#                       self.__normalize()
#                       try:
#                               return float(self.value)/self.table.total
#                       except ZeroDivisionError:
#                               return 0
#
#               def percentOfTotal(self):
#                       return int(self.fracOfTotal()*100+0.5)
#
#
#               def fracOfMax(self):
#                       self.__normalize()
#                       try:
#                               return float(self.value)/self.table.max
#                       except ZeroDivisionError:
#                               return 0
#
#               def fracOfRowMaxFrac(self):
#                       return self.fracOfRow()/self.table.maxofmaxfracsofrow
#
#
#               def fracOfRowMax(self):
#                       self.__normalize()
#                       try:
#                               return float(self.value)/self.table.rowmax[self.row]
#                       except ZeroDivisionError:
#                               return 0
#
#               def __repr__(self):
#                       return "Value(%d)"%self.value "stupid vim """

    def __init__(self, cols, rows):
        self.values=[[Table.Value(self, col, row, 0) for col in xrange(cols)] for row in xrange(rows)]
        self.columnlabels=['']*cols
        self.rowlabels=['']*rows
        self.cols=cols
        self.rows=rows
        self.total=0
        self.forcetotal=None
        self.normalized=False
        self.columnaxislabel=''
        self.rowaxislabel=''

    def duplicate(self):
        t=Table(self.cols, self.rows)
        for r in xrange(self.rows):
            t.setRowLabel(r, self.rowlabels[r])
            for c in xrange(self.cols):
                t.setValue(c, r, self.values[r][c].value)
                t.getValue(c, r).displayvalue=self.values[r][c].displayvalue
        for c in xrange(self.cols):
            t.setColumnLabel(c, self.columnlabels[c])
        t.setRowAxisLabel(self.getRowAxisLabel())
        t.setColumnAxisLabel(self.getColumnAxisLabel())
        return t

    def asPercentOfConstant(self, constant):
        t=self.duplicate()
        if constant == 0:
            constant=1
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                v=t.getValue(c, r)
                v.value=v.value/constant
                v.displayvalue=str(int(v.value*100+0.5))+'%'
        return t

    def asPercentOfTotal(self):
        total=0
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                v=self.getValue(c, r)
                total+=v.value
        if total == 0:
            total=1
        return self.asPercentOfConstant(total)

    def asPercentOfRow(self):
        t=self.duplicate()
        for r in xrange(self.rows):
            rowtotal=0
            for c in xrange(self.cols):
                v=t.getValue(c, r)
                rowtotal+=v.value
            if rowtotal == 0:
                rowtotal=1
            for c in xrange(self.cols):
                v=t.getValue(c, r)
                v.value=v.value/rowtotal
                v.displayvalue=str(int(v.value*100))+'%'
        return t

    def asFracOfRow(self):
        t=self.duplicate()
        for r in xrange(self.rows):
            rowtotal=0
            for c in xrange(self.cols):
                v=self.getValue(c, r)
                rowtotal+=v.value
            for c in xrange(self.cols):
                v=t.getValue(c, r)
                try:
                    v.frac=v.value/rowtotal
                except ZeroDivisionError:
                    v.frac=0
        t.normalized=True
        return t


#       def setTotal(self, t):
#               """Sets a total value which lies outside the table"""
#               self.forcetotal=t

    def normalize(self):
        """Compute the max in the table and the total of each row"""
        if self.normalized:
            return
        max=0
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                v=self.getValue(c, r)
                if not v:
                    continue
                if v.value > max:
                    max=v.value
        if max == 0:
            max=1
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                v=self.getValue(c, r)
                v.frac=v.value/max

#       def old_normalize(self):
#               self.max=0
#               self.total=0
#               self.rowtotals=[0]*self.rows
#               self.rowmax=[0]*self.rows
#               for r in xrange(self.rows):
#                       for c in xrange(self.cols):
#                               v=self.getValue(c, r)
#                               if not v:
#                                       continue
#                               if v.value > self.max:
#                                       self.max=v.value
#                               if v.value > self.rowmax[r]:
#                                       self.rowmax[r]=v.value
#                               self.total+=v.value
#                               self.rowtotals[r]+=v.value
#               self.rowtotalsmax=max(self.rowtotals)
#               self.maxfracsofrow=[self.rowmax[r]/(self.rowtotals[r]+0.0000001) for r in xrange(self.rows)]
#               self.maxofmaxfracsofrow=max(self.maxfracsofrow)
#               if self.forcetotal != None:
#                       self.total=self.forcetotal
#               self.normalized=True

    def transpose(self):
        oldvals=self.values
        self.values=[[oldvals[row][col] for row in xrange(self.rows)] for col in xrange(self.cols)]
        rs=self.rows
        self.rows=self.cols
        self.cols=rs
        rls=self.rowlabels
        self.rowlabels=self.columnlabels
        self.columnlabels=rls
        self.normalized=False
        ral=self.rowaxislabel
        self.rowaxislabel=self.columnaxislabel
        self.columnaxislabel=ral

    def transposed(self):
        t=self.duplicate()
        t.transpose()
        return t

    def getValue(self, col, row):
        return self.values[row][col]

    def setValue(self, col, row, val):
        self.values[row][col]=Table.Value(self, col, row, val)
        self.normalized=False

    def addToValue(self, col, row, val):
        if not self.values[row][col]:
            self.setValue(col, row, 0)
        v=self.values[row][col]
        self.setValue(col, row, v.value+val)
        self.normalized=False

    def filter_rows(self, nums):
        rs = []
        labels = []
        for r in nums:
            rs.append(self.getRow(r))
            labels.append(self.getRowLabel(r))
        t = Table(self.cols, len(nums))
        t.values = rs
        t.rowlabels = labels
        t.columnlabels = self.columnlabels[:]
        t.columnaxislabel = self.columnaxislabel
        t.rowaxislabel = self.rowaxislabel
        return t

    def getRow(self, row):
        return self.values[row][:]

    def getColumn(self, col):
        return [row[col] for row in self.values]

    def setColumnLabel(self, col, label):
        self.columnlabels[col]=label

    def setRowLabel(self, row, label):
        self.rowlabels[row]=label

    def getColumnLabel(self, col):
        return self.columnlabels[col]

    def getRowLabel(self, col):
        return self.rowlabels[col]

    def setColumnLabels(self, labels):
        if len(labels) !=  self.cols:
            raise ValueError("Incompatible size for column labels")
        self.columnlabels=labels

    def setRowLabels(self, labels):
        if len(labels) !=  self.rows:
            raise ValueError("Incompatible size for row labels")
        self.rowlabels=labels

    def setRowAxisLabel(self, l):
        self.rowaxislabel=l

    def setColumnAxisLabel(self, l):
        self.columnaxislabel=l

    def getRowAxisLabel(self):
        return self.rowaxislabel

    def getColumnAxisLabel(self):
        return self.columnaxislabel

    def __repr__(self):
        return "Table("+str(self.values)+")"
