"""Utility functions and objects"""
from collections import defaultdict
import curses


def buildlinesdict(lines, defaultstr='~', default_attr=curses.A_NORMAL):
    """build a default dict with schema:
    index --> (line or <defaultstr>, curses str attributes)
    The default string makes scrolling past the edge of the file much more
    graceful.
    I.e. having a default value rather than handling IndexError and then
    returning the default string.
    This function will add a default or the provided attribute to each line.
    The lines can be further decorated at later times by logically OR-ing in
    other attributes to the attribute set here."""
    ret = defaultdict(lambda: (defaultstr, default_attr))
    for idx, bline in enumerate(lines):
        if isinstance(bline, bytes):
            bline = bline.decode('UTF-8')
        ret[idx] = (bline, default_attr)
    return ret


# In this case I really do want an object pylint, but thanks...
# pylint: disable=R0903
class BidirectionalCycle(object):
    """A cycle iterator that can iterate in both directions (e.g. has next
    and prev).
    This is a simple object that supports the iterator protocol but it doesn't
    behave like one might expect a standard iterator to (e.g. a generator that
    lazily produces the next value) this object will keep the WHOLE LIST in
    memory, so use WITH CAUTION"""
    def __init__(self, list_seq, starting_index=0, no_wrap=False):
        self.current_index = self.init_index = starting_index
        # CURRENTLY ONLY SUPPORT LISTS
        assert isinstance(list_seq, list), 'Currently only supports lists'
        self.seq = list_seq
        self.no_wrap = no_wrap
        self.start_of_day = True

    def next(self):
        """Maintain support for python2 iterator"""
        return self.__next__()

    def __next__(self):
        """return the next item in the iteration"""
        self._check_len()
        if self.start_of_day:
            return self._start_of_day()

        self._move_index_next()
        next_item = self.seq[self.current_index]

        return next_item

    def prev(self):
        """return the previous item in the iteration"""
        self._check_len()
        if self.start_of_day:
            if self.no_wrap:
                return ''
            return self._start_of_day()

        self._move_index_prev()
        prev_item = self.seq[self.current_index]

        return prev_item

    def _move_index_next(self):
        """Move the index in the next direction"""
        # check if we need to wrap around to the beginning
        if self.current_index == len(self.seq) - 1:
            if self.no_wrap:
                return
            self.current_index = 0
        else:
            self.current_index = self.current_index + 1

    def _move_index_prev(self):
        """Move the index in the prev direction"""
        # check if we need to wrap around to the end
        if self.current_index == 0:
            if self.no_wrap:
                return
            self.current_index = len(self.seq) - 1
        else:
            self.current_index = self.current_index - 1

    def _check_len(self):
        """As itertools.cycle does, raise StopIteration if the sequence
        is empty"""
        if len(self.seq) == 0:
            raise StopIteration

    def _start_of_day(self):
        """print out the init_index of the sequence and set start_of_day to
        false"""
        self.start_of_day = False
        return self.seq[self.init_index]

    def __str__(self):
        return str(self.seq)

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.seq)

    def __contains__(self, item):
        return item in self.seq
