# -*- coding: utf-8 -*-
"""Extensions for supporting local filesystem transactional objects.
Objects may be created/modified/deleted."""

#class recycle_bin
import os
import shutil
from tran import TransactionObject


class TransactionFSObject(TransactionObject):
    """This class constitutes the base for filesystem transaction objects.
    The main problem with this element is that we **must** avoid the use of
    relative paths. For this pourpose, we need a base path provider"""
    def __init__(self, **kwargs):
        """init"""
        abspath = kwargs['file']
        #assert os.access(abspath, os.W_OK)  # test for write access
        #assert os.access(abspath, os.R_OK)  # test for read access
        self._mode_dir = os.path.isdir(abspath)
        self._uri = kwargs['uri']
        self._file = os.path.relpath(abspath, self._uri.dir)
        self._version = 0
        super(TransactionFSObject, self).__init__(**kwargs)

    @property
    def abs_file(self):
        """return the absolute file name"""
        try:
            return os.path.join(self._uri.dir, self._file)
        except:
            return self._file

    @property
    def version_file(self):
        """return the current version file"""
        path, name = os.path.split(self.abs_file)
        return os.path.join(path, '.{name}.{version}'.format(name=name, version=self._version))

    @property
    def tmp_file(self):
        """return temporally fname"""
        path, name = os.path.split(self.abs_file)
        return os.path.join(path, '.{name}.tmp'.format(name=name))

    def swap(self, f1, f2):
        """swap files"""
        print "swap {f1}<->{f2}\n".format(f1=f1, f2=f2)
        shutil.copyfile(f1, self.tmp_file)
        shutil.copyfile(f2, f1)
        shutil.copyfile(self.tmp_file, f2)
        os.remove(self.tmp_file)

    def SaveState(self):
        """Save state"""
        # The version of the file store changes and open a new version
        #print "saving state of version : {self._version}\n".format(self=self)
        try:
            if self._mode_dir:
                super(TransactionFSObject, self).SaveState()
                return
            shutil.copyfile(self.abs_file, self.version_file)
            self._version = self._version + 1
        except:
            pass
        super(TransactionFSObject, self).SaveState()

    def OnUndoRedoChanged(self):
        """Do a transactional action"""
        if not self.InUndoRedo():
            return
        if not self._mode_dir:
            try:
                if self.InUndo():
                    if not os.path.exists(self.abs_file):
                        if os.path.exists(self.version_file):
                            os.remove(self.version_file)
                    else:
                        shutil.copyfile(self.abs_file, self.version_file)
                    self._version = self._version - 1
                    if os.path.exists(self.version_file):
                        shutil.copyfile(self.version_file, self.abs_file)
                    else:
                        os.remove(self.abs_file)
                    self._version = self._version + 1
                elif self.InRedo():
                    if os.path.exists(self.version_file):
                        shutil.copyfile(self.version_file, self.abs_file)
                    else:
                        os.remove(self.abs_file)
            except:
                pass

    def OnUndoRedoLoaded(self):
        """Do initial load"""
        print "OnUndoRedoLoaded called"
        self._version = 0

    def OnUndoRedoRemoving(self):
        """Do a transactional action"""
        # this operation is tentative:
        try:
            if self._mode_dir:
                os.rename(self.abs_file, self.tmp_file)
            else:
                shutil.copyfile(self.abs_file, self.version_file)
                os.remove(self.abs_file)
        except:
            pass

    def OnUndoRedoAdd(self):
        """Do a transactional action"""
        if not self.InUndoRedo():
            return
        try:
            if self._mode_dir:
                os.rename(self.tmp_file, self.abs_file)
            else:
                shutil.copyfile(self.version_file, self.abs_file)
        except:
            pass

    def Dispose(self):
        """When an object is finally removed from the stack,
        the associated external resources may be also released."""
        try:
            if self._mode_dir:
                f = self.tmp_file
                if os.access(f, os.W_OK):
                    shutil.rmtree(f)
            else:
                if self._version:
                    os.remove(self.version_file)
        except:
            pass
