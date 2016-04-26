import  os, hashlib, yaml
from pathlib import PosixPath
from colorama import init
from colorama import Fore, Back, Style

init()


class PyAudioDupleyFinder:
    filelist = []
    duolfilelist = []

    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self.db = FileHashShelve(root_path)
        self.analyzed_list = {}

    def create_file_list(self, root_path, extensions, min_filesize, debug):
        self.filelist = [p for p in PosixPath(root_path).rglob('**/*') if
                (p.name.endswith(extensions) and p.stat().st_size >= min_filesize)]
        return self.filelist

    def get_duplicate_list(self):
        return self.db.get_duplfile()

    def analyze(self, hash_type='MD5', debug=False, progressbar=None):
        if hash_type not in hashlib.algorithms_available:
            raise AttributeError('Not supported hash algorithm')
        for f in self.filelist:
            h = hashlib.new(hash_type)
            h.update(open(str(f), 'rb').read())
            f_hash = h.hexdigest()
            if debug:
                print(Fore.WHITE, f.name)
                print(Style.DIM, f_hash, Style.RESET_ALL)
            self.db.add(f_hash, str(f))
            if progressbar:
                progressbar.update()

    def save_duplicates_to_yaml(self, duplfile):
        yaml.dump(duplfile, open(os.getcwd() + '/pyaudiodupleyfind-result.yaml', 'w'),
                  explicit_start=True, default_flow_style=False, indent=4)


class FileHashShelve:
    def __init__(self, root_path):
        super().__init__()
        self.db = dict({})
        self.root_path = root_path

    def size(self):
        return len(self.db)

    def add(self, filehash, path):
        if filehash in self.db:
            self.db[filehash].add_filepath(path)
        else:
            duplfile = DuplFile(filehash, self.root_path)
            duplfile.add_filepath(path)
            self.db[filehash] = duplfile

    def get_duplfile(self):
        return [self.db[a] for a in self.db if self.db[a].has_duplicates()]


class DuplFile:
    def __init__(self, file_hash, root_path):
        self.file_hash = file_hash
        self.root_path = root_path
        self.files = []
        self.file_size = 0

    def add_filepath(self, path):
        if path not in self.files:
            f_stat = os.stat(path)
            if len(self.files) == 0:
                self.file_size += f_stat.st_size
            self.files.append(path)

    def has_duplicates(self):
        return len(self.files) > 1

    def get_file_list(self):
        return self.files

    def get_file_hash(self):
        return self.file_hash

    def save_as_yaml(self):
        filepath = os.getcwd()
        yaml.dump(self, open(filepath + '/pyaudiodupleyfind-result.yaml', 'w'),
                  explicit_start=True, default_flow_style=False, indent=4)

    def get_size_recovery(self):
        if len(self.files) > 1:
            return self.file_size * (len(self.files) - 1)
        else:
            return 0

    def __repr__(self):
        return "Filehash: " + self.file_hash + "\nFiles:\n\t" + "\n\t".join(self.files)
