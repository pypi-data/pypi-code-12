import logging, os, hashlib, yaml, pprint
from abc import ABCMeta
from builtins import property
from pathlib import PosixPath
from datetime import timedelta, datetime
import click
import pyprind
from colorama import init
from colorama import Fore, Back, Style
import humanfriendly
from tabulate import tabulate
from tqdm import tqdm

init()

class AbstractPyAudioDupleyFinder():
    metaclass = ABCMeta
    LOG_FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_LEVER = logging.DEBUG
    BLOCKSIZE = 65536
    filelist = []

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        log_stream_handler = logging.StreamHandler()
        log_stream_handler.setFormatter(self.LOG_FORMATTER)
        log_stream_handler.setLevel(self.LOG_LEVER)
        self.logger.addHandler(log_stream_handler)
        self.pp = pprint.PrettyPrinter(indent=2)


class PyAudioDupleyFinder(AbstractPyAudioDupleyFinder):
    def __init__(self, path, extensions, debug=False):
        super().__init__()
        self.root_path = path
        self.db = FileHashShelve(path)
        self.filelist = self.__create_file_list(path, extensions)
        self.debug = debug

    @staticmethod
    def __create_file_list(path, extensions):
        root_audiodir = PosixPath(path)
        if root_audiodir.exists() and root_audiodir.is_dir():
            return [f for f in [fe for fe in sorted(root_audiodir.glob('**/*')) if fe.is_file()] if
                    f.name.endswith(extensions)]
        else:
            return []

    def filelist_size(self):
        return len(self.filelist)

    def print_file_list(self):
        for f in self.filelist:
            print(f)
            f_stat = os.stat(str(f))
            print(f_stat.st_size)
        print(Fore.YELLOW + 'File count: ' + str(len(self.filelist)))
        print(Style.RESET_ALL)

    def get_duplicate_list(self):
        return self.db.get_duplfile()

    def print_duplicate_list(self, duplfile):
        for dup in duplfile:
            print("%s %s" % (humanfriendly.format_size(dup.get_size_recovery()), dup.file_hash))
            for d in dup.files:
                print("\t- %s" % d)
            print()
        print(Style.RESET_ALL)

    def analyze(self, hash_type='MD5', debug=False):
        if hash_type not in hashlib.algorithms_available:
            raise AttributeError('Not supported hash algorithm')
        start_time = datetime.now()
        print('Analyzing ' + str(len(self.filelist)) + ' files with ' + hash_type + ' algorithm')
        bar = pyprind.ProgBar(len(self.filelist), monitor=True, width=100)
        for f in self.filelist:
            h = hashlib.new(hash_type)
            h.update(open(str(f), 'rb').read())
            f_hash = h.hexdigest()
            if debug:
                print(Fore.WHITE, f.name)
                print(Style.DIM, f_hash, Style.RESET_ALL)
            self.db.add(f_hash, str(f))
            bar.update()
        end_time = datetime.now()
        time_delta = end_time - start_time
        print(Fore.GREEN, "Finished alayzing in " + str(time_delta.seconds) + ' seconds and '
              + str(time_delta.microseconds) + ' microseconnds')
        print(Style.RESET_ALL)
        click.clear()
        print(Style.DIM, bar)
        print(Style.RESET_ALL)

    def save_duplicates_to_yaml(self, duplfile):
        yaml.dump(duplfile, open(os.getcwd() + '/pyaudiodupleyfind-result.yaml', 'w'),
                  explicit_start=True, default_flow_style=False, indent=4)
        print('Duplicate list saved to file ' + self.root_path + '/duplicate_list.yaml')

    @staticmethod
    def get_hash_algorithms():
        return hashlib.algorithms_available


class FileHashShelve(AbstractPyAudioDupleyFinder):
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

    @property
    def get_file_list(self):
        return self.files

    @property
    def get_file_hash(self):
        return self.file_hash

    def save_as_yaml(self):
        filepath = os.getcwd()
        yaml.dump(self, open(filepath + '/pyaudiodupleyfind-result.yaml', 'w'),
                  explicit_start=True, default_flow_style=False, indent=4)

    def get_size_recovery(self):
        if len(self.files) > 1:
            return self.file_size * (len(self.files)-1)
        else:
            return 0

    def __repr__(self):
        return "Filehash: " + self.file_hash + "\nFiles:\n\t" + "\n\t".join(self.files)
