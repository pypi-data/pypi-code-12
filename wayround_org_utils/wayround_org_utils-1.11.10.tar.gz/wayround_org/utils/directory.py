
class Directory:

    def __init__(self, parent=None):
        self._files = {}
        self._parent = parent
        return

    @property
    def parent(self):
        return self._parent

    def get_this_dir_path(self):
        path = []

        p = self

        while p is not None:
            path.insert(0, p)
            p = p.parent

        return path

    def get_root(self):
        ret = self
        while True:
            if ret.parent is None:
                break
            ret = ret.parent
        return ret

    def mkdir(self, name):
        self._files[name] = Directory(self)
        return self._files[name]

    def mkfile(self, name, value=None):
        self._files[name] = File(init_value=value, parent=self)
        return self._files[name]

    def delete(self, name):
        if name in self._files:
            del self._files[name]
        return

    def listdir(self):
        return list(self._files.keys())

    def listdir2(self):
        return self.dirnames(), self.filenames()

    def dirnames(self):
        ret = []
        for i in self.listdir():
            if type(self._files[i]) == Directory:
                ret.append(i)
        return ret

    def filenames(self):
        ret = []
        for i in self.listdir():
            if type(self._files[i]) == File:
                ret.append(i)
        return ret

    def dirs(self):
        ret = []
        for i in self.listdir():
            if type(self._files[i]) == Directory:
                ret.append(self._files[i])
        return ret

    def isdir(self):
        return True

    def isfile(self):
        return False

    def getpath(self, path_lst, create_dirs=False):
        """
        if path is not found and create_dir is True, then the path is created
            as dir
        None returned in case of error
        """
        ret = None

        if len(path_lst) != 0:
            name = path_lst[0]
            if name == '/':
                ret = self.get_root()
            elif name in self:
                ret = self[name]
            else:
                if create_dirs:
                    ret = self.mkdir(name)
                else:
                    ret = None
        else:
            ret = self

        if ret is not None and len(path_lst) != 0:
            rem_path = path_lst[1:]
            if len(rem_path) == 0:
                pass
            else:
                ret = ret.getpath(rem_path, create_dirs=create_dirs)

        return ret

    def walk(self):
        folders = self.dirnames()
        files = self.filenames()

        path = self.get_this_dir_path()

        yield path, folders, files

        for i in folders:
            for j in self[i].walk():
                yield j
        return

    def __contains__(self, name):
        return name in self._files

    def __getitem__(self, name):
        return self._files[name]


class File:

    def __init__(self, init_value=None, parent=None):
        self._v = init_value
        self._parent = parent
        return

    @property
    def parent(self):
        return self._parent

    def isdir(self):
        return False

    def isfile(self):
        return True

    def get_value(self):
        return self._v

    def set_value(self, v):
        self._v = v
        return
