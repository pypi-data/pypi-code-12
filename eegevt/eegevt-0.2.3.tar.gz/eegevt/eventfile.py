import os.path
from collections import namedtuple


class EventFile:
    """docstring for EventFile"""
    def __init__(self, filename):
        self.source = os.path.abspath(filename)
        self.root, self.ext = os.path.splitext(filename)
        self.raw = self._read()

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

    def mod_code(self, linenum, newcode):
        '''Modify the stored event code on linenum to be newcode'''
        self.events[linenum] = self.events[linenum]._replace(code=newcode)
        if self.filetype == 'BESA':
            self.events[linenum] = \
                    self.events[linenum]._replace(codestr='Trig. ' + newcode)

    def _read(self):
        """Read the text from the event file into memory, sniffing file type
        as we go
        """
        with open(self.source, 'r') as ef:
            lines = ef.read().splitlines()
        self._sniff(lines[0])
        self._split(lines)
        return lines

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
                ef.write('\n'.join(['\t'.join(d) for d in self.events]) + '\n')
                return
            if self.filetype == 'Neuroscan_2':
                ef.write('\n'.join([' '.join(d) for d in self.events]) + '\n')
                return


def load_efile(filepath):
    """Load and return an EventFile object"""
    return EventFile(filepath)


def save_efile(efile, appendtext='_recoded', **kwargs):
    """save the event file with an optional filename append string"""
    efile.root += appendtext
    efile._save(**kwargs)
