# -*- coding: utf-8 -*-

"""The mission of logger is create an action logger suitable for creating operations
logs that will be useful (for example, for documenting operations)
"""
import wx
import time
import os


LOG_START = False  # whether register or not
LOG_END = False  # whether register or not


class loggerEntry(object):
    """Represents a single logger entry"""
    def __init__(self, text, reference=None):
        """Initialize logger"""
        self._reference = reference
        self._text = text
        self._time = time.strftime('%d-%m-%Y %H:%M:%S')
        wx.LogMessage(text)
        super(loggerEntry, self).__init__()

    @property
    def reference(self):
        """Return the reference"""
        return self._reference

    @property
    def status(self):
        """Return the stack status"""
        import tran
        return tran.TransactionalStack.instance.TransactionStatus(self._reference)

    def __str__(self):
        '''Return an string representation of the entry'''
        return '[{self._time}] {self._text}'.format(self=self)


class logger(object):
    """Logger that holds the operations"""

    def __init__(self, **kwargs):
        """Initialize logger"""
        self._log = []
        self._backlog = []
        self._filter = kwargs.get('filter', None)  # the filter
        self._fname = None  # the file name
        self._queue = []  # next logger queue
        super(logger, self).__init__()

    def pushLogger(self, another):
        """Append another logger"""
        self._queue.append(another)

    def popLogger(self, another):
        """Remove logger from queue"""
        if another in self._queue:
            i = self._queue.index(another)
            del self._queue[i]

    def addEntry(self, text, reference=None):
        """Append new log entry"""
        self._backlog = []
        self._log.append(loggerEntry(text, reference))

    def __call__(self, command, transaction=None):
        """Interface for transaction handler"""
        if command == 'start':
            self._log = []
            if LOG_START:
                self.addEntry('====== STARTING LOG ======')
            else:
                self._backlog = []
            return
        if command == 'commit':
            if self._filter is None or self._filter(transaction):
                self.addEntry(transaction._name, hash(object))
                #propagate
                for log in self._queue:
                    log(command, transaction)
        elif command == 'undo':
            assert(len(self._log) > 0)
            entry = self._log.pop()
            self._backlog.append(entry)
            #propagate
            for log in self._queue:
                if not len(log._log):
                    continue
                if entry.reference() == log._log[-1].reference:
                    log('undo')
        elif command == 'redo':
            assert(len(self._backlog) > 0)
            entry = self._backlog.pop()
            self._log.append(entry)
            for log in self._queue:
                if not len(log._backlog):
                    continue
                if entry.reference() == log._backlog[-1].reference:
                    log('redo')
        elif command == 'end':
            self._log = []
            if LOG_END:
                self.addEntry('====== ENDING LOG ======')
            else:
                self._backlog = []

    def SetFile(self, fname):
        """Sets the log file"""
        self._fname = fname

    def Dump(self):
        """This command only dumps current logs (not backlogs)"""
        #propagate
        for log in self._queue:
            log.Dump()
        if not self._fname:
            return False
        try:
            fname = os.path.realpath(self._fname)
            f = open(fname, 'w+')
            for i in range(0, len(self._log)):
                f.write('{logline}\n'.format(logline=str(self._log[i])))
            f.close()
        except:
            return False


