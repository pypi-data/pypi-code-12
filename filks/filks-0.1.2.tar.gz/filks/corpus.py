import zipfile
import fnmatch
import glob
import os, os.path
import sys
from filks.tagged_text import TaggedText
from filks.random2 import weighted_choice


SUBPATH_SEP = '#'
PATH_SIZE_LIMIT = 4096
FILENAME_SIZE_LIMIT = 255
NLTK_PREFIX = 'nltk.'




def Corpus(path, pattern=None):
    path = path.strip() if path else None
    pathname = _fs_path_name(path) if path else None
    if not pathname:
        return NltkCorpus('brown')
    elif pathname == '-':
        return RawTextCorpus(sys.stdin.read())
    elif pathname.startswith(NLTK_PREFIX):
        return NltkCorpus(pathname[len(NLTK_PREFIX):])
    elif not _probably_filename(pathname):
        return RawTextCorpus(path)
    elif os.path.isdir(pathname):
        return FolderCorpus(path, pattern)
    elif os.path.isfile(pathname):
        return _get_file_corpus(path, pattern)
    else:
        raise RuntimeError('File not found: `{}`'.format(pathname))


def _fs_path_name(path):
    return path.split(SUBPATH_SEP)[0]


def _get_file_corpus(path, pattern=None):
    pathname = _fs_path_name(path)
    with open(pathname, 'r') as f:
        initial_data = f.read(10)
    if initial_data.startswith('PK'):
        return ZippedCorpus(path, pattern)
    else:
        return SingleFileCorpus(pathname, pattern)


def _probably_filename(path):
    if len(path) > PATH_SIZE_LIMIT:
        return False
    elif os.path.exists(path):
        return True
    elif path.count('. ') >= 3 or path.count('\n') >= 3 or path.count(', ') >= 3:
        return False
    elif max(len(filename) for filename in path.split('/')) > FILENAME_SIZE_LIMIT:
        return False
    else:
        return True


class SingleFileCorpus(object):
    def __init__(self, path, pattern=None):
        self.__path = path

    def random_text(self, dictionary=None, **kwargs):
        return TaggedText(open(self.__path, 'r'), dictionary=dictionary, **kwargs)


class RawTextCorpus(object):
    def __init__(self, text):
        self.__text = text

    def random_text(self, dictionary=None, **kwargs):
        return TaggedText(self.__text, dictionary=dictionary, **kwargs)


class FolderCorpus(object):
    def __init__(self, path, pattern='**'):
        if os.path.exists(path) and os.path.isdir(path):
            self.__path = '{}/{}'.format(path, pattern)
        else:
            self.__path = path
        self.__files = {
            filename: os.path.getsize(filename)
            for filename in glob.iglob(self.__path, recursive=True)
        }.items()

    def random_text(self, dictionary=None, **kwargs):
        filename = weighted_choice(self.__files)
        return TaggedText(open(filename, 'r'), dictionary=dictionary, **kwargs)


class ZippedCorpus(object):
    DEFAULT_PATTERN = '*/c*'
    def __init__(self, path, pattern=None):
        if not pattern and SUBPATH_SEP in path:
            path, pattern = path.split(SUBPATH_SEP, 1)
        else:
            pattern = pattern or self.DEFAULT_PATTERN

        self.__path = path
        patterns = [p.strip() for p in pattern.split(',')]
        with zipfile.ZipFile(path) as z:
            # Weight by file size (approx number of words in file)
            self.__files = {
                info.filename: info.file_size
                for info in z.infolist()
                if any(fnmatch.fnmatch(info.filename, pattern) for pattern in patterns)
            }.items()

    def random_text(self, dictionary=None, **kwargs):
        filename = weighted_choice(self.__files)
        with zipfile.ZipFile(self.__path) as z:
            return TaggedText(z.read(filename).decode(), dictionary=dictionary, **kwargs)


class NltkCorpus(object):
    def __init__(self, nltk_corpus='brown', pattern='**'):
        if isinstance(nltk_corpus, str):
            import nltk.corpus
            nltk_corpus = getattr(nltk.corpus, nltk_corpus)
        self.__corpus = nltk_corpus
        self.__files = {
            fileid: 1
            for fileid in self.__corpus.fileids()
        }.items()

    def random_text(self, dictionary=None, **kwargs):
        filename = weighted_choice(self.__files)
        for attr in ('tagged_words', 'words', 'raw'):
            text = getattr(self.__corpus, attr, lambda X: None)(filename)
            if text:
                return TaggedText(text, dictionary=dictionary, **kwargs)
        else:
            raise NotImplementedError('Could not find text in corpus?')
