import os.path
from collections import namedtuple


class EventFile:
    """docstring for EventFile"""
    def __init__(self, filename):
        if os.path.isfile(filename):
            self.source = os.path.abspath(filename)
            self.root, self.ext = os.path.splitext(filename)
            self.raw = self._read()
        else:
            raise FileNotFoundError('Event file not found', filename)

    def _sniff(self, firstline):
        """Sniff the file type (creating software)"""
        if self.ext == '.evt' and firstline.startswith('Tmu'):
            self.filetype = 'BESA'
            return
        if self.ext == '.ev2':
            self.filetype = 'Neuroscan_2'
            return
        raise ValueError('Undetected type', 'Extension:' + self.ext,
                         'First Line: ' + firstline)

    def _check(self):
        """Test for consistency (all rows have same number of columns """
        if not all(len(d) == len(self.events[0]) for d in self.events):
            raise ValueError('Line has unexected number of elements')

    def _splitBESA(self, lines):
        """Split lines in a BESA specific way"""
        self.header = [h.strip() for h in lines[0].split('\t')]
        if self.header != ['Tmu', 'Code', 'TriNo', 'Comnt']:
            raise ValueError('BESA header format not expected')
        Event = namedtuple('Event', 'time, typecode, code, codestr')
        line2 = [d.strip() for d in lines[1].split('\t')]
        if line2[1] == '41':
            self.extra = line2
            self.timestamp = line2[2]
            lines = lines[2:]
        else:
            self.extra = None
            lines = lines[1:]
        self.events = [Event(*[d.strip() for d in l.split('\t')]) for l in lines]

    def _splitNS2(self, lines):
        """split lines in a Neuroscan ev2 specific way"""
        Event = namedtuple('Event', 'evtnum, code, rcode, racc, rlat, time')
        self.events = [Event(*[d.strip() for d in l.split()]) for l in lines]

    def _split(self, lines):
        """Split lines in a fileformat dependant way and extract header"""
        if self.filetype == 'BESA':
            self._splitBESA(lines)
        elif self.filetype == 'Neuroscan_2':
            self._splitNS2(lines)
        else:
            raise NotImplementedError('Cannot find split method for ',
                                      self.filetype)

    def mod_code(self, linenum, newcode):
        '''Modify the stored event code on linenum to be newcode'''
        self.events[linenum].code = newcode
        if self.filetype == 'BESA':
            self.events[linenum].codestr = 'Trig. ' + newcode

    def _read(self):
        """Read the text from the event file into memory, sniffing file type
        as we go
        """
        with open(self.source, 'r') as ef:
            lines = ef.read().splitlines()
        self._sniff(lines[0])
        self._split(lines)
        self._check()

    def _save(self, writemode='x'):
        """Save the current data to file (build from root/ext) and throw error
        if file exists and overwrite == False"""
        with open(self.root + self.ext, writemode) as ef:
            if self.filetype == 'BESA':
                ef.write('\t'.join(self.header))
                ef.write('\n')
                if self.extra:
                    ef.write('\t'.join(self.extra))
                    ef.write('\n')
                ef.write('\n'.join(['\t'.join(d) for d in self.events]))
                return
            if self.filetype == 'Neuroscan_2':
                ef.write('\n'.join([' '.join(d) for d in self.events]))
                return
            raise ValueError('Unhandled type', self.filetype)


def load_efile(filepath):
    """Load and return an EventFile object"""
    return EventFile(filepath)


def save_efile(efile, appendtext='_recoded', **kwargs):
    """save the event file with an optional filename append string"""
    efile.root += appendtext
    efile._save(**kwargs)
