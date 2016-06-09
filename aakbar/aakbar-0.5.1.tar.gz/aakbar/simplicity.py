# -*- coding: utf-8 -*-
'''Simplicity masking and scoring classes.
'''

# external packages
import numpy as np
import pandas as pd

# module imports
from .common import *
from . import cli, get_user_context_obj, logger

class SimplicityObject(object):
    '''Define the interfaces needed to make simplicity calculations.

    '''
    def __init__(self, default_cutoff=DEFAULT_SIMPLICITY_CUTOFF):
        self.cutoff = default_cutoff
        self.k = None
        self.label = 'null'
        self.desc = 'no simplicity calculation'
        self.testcases = [('     non-repeated', 'ABCDEFGHIJ'),
                          ('Simple Repeated Letters', ''),
                          ('15 in a row', 'AAAAAAAAAAAAAAA')
                          ]


    def set_cutoff(self, cutoff):
        '''Set the lower bound on simplicity.

        :param cutoff:  Cutoff value, lower results in more sequence masked.
        :return: None
        '''
        if cutoff < 2:
            logger.error('Simplicity cutoff must be >=2.')
            sys.exit(1)
        else:
            self.cutoff = cutoff


    def set_k(self, k):
        '''Set the k value over which rolling scores are summed.

        :param k: Number of characters in window.
        :return:  None.
        '''
        if k < 2:
            logger.error('k must be >=2')
            sys.exit(1)
        else:
            self.k = k


    def mask(self,seq):
        '''Returns the input string.

        :param seq: Input string.
        :return: Masked copy of input string.  Must be the same length.
        '''
        return seq


    def score(self, seq):
        '''Count the number masked (by lower-case) over a window.

        :param seq: String of characters.
        :param window_size: Size of window over which to calculate.
        :return: Integer array of counts.
        '''
        is_lower = pd.Series([int(char.islower()) for char in to_str(seq)])
        return is_lower.rolling(window=self.k).sum()[self.k-1:].astype(int)


class RunlengthSimplicity(SimplicityObject):
    '''Define simplicity by the number of repeated letters.

    '''
    def __init__(self, default_cutoff=DEFAULT_SIMPLICITY_CUTOFF):
        super().__init__(default_cutoff=default_cutoff)
        self.label = 'runlength'
        self.desc = 'runlength (repeated characters)'
        self.testcases += [
                 ('Simple Repeated Letters', ''),
                 ('double, beginning', 'AABCDEFGHI'),
                 (' double in middle', 'ABCDEEFGHI'),
                 ('double at end', 'ABCDEFGHII'),
                 ('double everywhere', 'AABCDDEFGG'),
                 ('triple, beginning', 'AAABCDEFGH'),
                 (' triple in middle', 'ABCDEEEFGH'),
                 ('triple at end', 'ABCDEFGIII'),
                 ('quad in middle', 'ABCDEEEEFG'),
                 ('longer string with insert',
                  'AAAAAAABCDEFGHIJKLLLLLLL'),
                 #
                 ('Mixed Patterns', ''),
                 ('mixed repeat', 'BCAABCABCA')
        ]


    def _runlength(self, s):
        return [all([s[i+j+1] == s[i] for j in range(self.cutoff-1)])
                for i in range(len(s)-self.cutoff+1)]


    def mask(self,seq):
        '''Mask high-simplicity positions in a string.

        :param s: Input string.
        :return: Input string with masked positions changed to lower-case.
        '''
        for pos in [i for i, masked in
                    enumerate(self._runlength(to_str(seq).upper()))
                    if masked]:
            if isinstance(seq, str): #strings need to have whole length set
                seq = seq[:pos] +seq[pos:pos+self.cutoff].lower() + seq[pos+self.cutoff:]
            else:
                seq[pos:pos+self.cutoff] = to_str(seq[pos:pos+self.cutoff]).lower()
        return seq



class LetterFrequencySimplicity(SimplicityObject):
   '''Define simplicity by the number of repeated letters.

   '''
   def __init__(self,
                default_cutoff=DEFAULT_SIMPLICITY_CUTOFF,
                window_size=None):
       global config_obj
       super().__init__(default_cutoff=default_cutoff)
       if window_size is None:
           try:
               self.window_size = config_obj.config_dict['letterfreq_window']
           except KeyError:
               self.window_size = DEFAULT_LETTERFREQ_WINDOW
       else:
           self.window_size = window_size
       self.label = 'letterfreq%d' %self.window_size
       self.desc = 'letter frequency in window of %d residues'%self.window_size
       self.testcases += [
                 ('Simple Repeated Letters', ''),
                 ('double, beginning', 'AABCDEFGHI'),
                 ('double in middle', 'ABCDEEFGHI'),
                 ('double at end', 'ABCDEFGHII'),
                 ('double everywhere', 'AABCDDEFGG'),
                 ('triple, beginning', 'AAABCDEFGH'),
                 ('triple in middle', 'ABCDEEEFGH'),
                 ('triple at end', 'ABCDEFGIII'),
                 ('quad in middle', 'ABCDEEEEFG'),
                 #
                 ('Pattern Repeats', ''),
                 ('doublet repeat', 'ABABABABAB'),
                 ('triplet repeat', 'ABCABCABCA'),
                 ('quad repeat', 'ABCDABCDAB'),
                 ('penta repeat', 'ABCDEABCDE'),
                 #
                 ('Mixed Patterns', ''),
                 ('mixed repeat', 'BCAABCABCA'),
                          ('long repeats with insert',
                           'SATANSPRAWNSATANSPRAWNSATANSPRAWNSAOPQTUVWXYZSATANSPAWNSATANSPAWN')

    ]


   def mask(self,seq):
        '''Mask high-simplicity positions in a string.

        :param s: Input string.
        :return: Input string with masked positions changed to lower-case.
        '''
        out_str = to_str(seq)
        end_idx = len(out_str) - 1
        byte_arr = np.array([char for char in to_bytes(out_str.upper())])
        mask_positions = set()
        #
        # test character by character for number of occurrances over window
        #
        for char in set(byte_arr): # test character by character
            char_positions = list(np.where(byte_arr == char)[0])
            while len(char_positions) >= self.cutoff:
                testpos = char_positions.pop(0)
                next_positions = char_positions[:self.cutoff-1]
                if next_positions[-1] - testpos < self.window_size:
                    mask_positions = mask_positions.union(set([testpos] + next_positions))
        #
        # mask everything
        #
        for pos in mask_positions:
            out_str = out_str[:pos] + out_str[pos].lower() + out_str[pos+1:]

        if isinstance(seq, str): # strings need to have whole length set
            seq = out_str
        else:                    # may be MutableSeq that needs lengths
            seq[:end_idx] = out_str[:end_idx]
        return seq


#
# Instantiations of classes.
#
NULL_SIMPLICITY = SimplicityObject()
RUNLENGTH_SIMPLICITY = RunlengthSimplicity()
LETTERFREQ_SIMPLICITY = LetterFrequencySimplicity()

@cli.command()
@click.option('--cutoff', default=DEFAULT_SIMPLICITY_CUTOFF, show_default=True,
              help='Maximum simplicity to keep.')
@click.option('-k', default=DEFAULT_K, show_default=True,
              help='k-mer size for score calculation.')
def demo_simplicity(cutoff, k):
    '''Demo self-provided simplicity outputs.

    :param cutoff: Simplicity value cutoff, lower is less complex.
    :param window_size: Window size for masking computation..
    :return:
    '''
    user_ctx = get_user_context_obj()
    simplicity_obj = user_ctx['simplicity_object']
    simplicity_obj.set_cutoff(cutoff)
    logger.info('Simplicity function is %s with cutoff of %d.',
                simplicity_obj.desc, cutoff)
    simplicity_obj.set_k(k)
    logger.info('           Mask window demo for %d-mers:', k)
    mask_test = 'AAAAAAAAAAaaaaAAAAAAAAAAAaaaaaAAAAAAAAAAAAaaaaaaAAAAAAAAAAAAAaaaaaaaAAAAAAAAAAAAAA'
    logger.info('      in: %s\n S-score: %s\n', mask_test,
                ''.join(['%X'%i for i in
                         simplicity_obj.score(mask_test)]))
    for desc, case in simplicity_obj.testcases:
        if case is '':
            logger.info('              %s', desc)
        else:
            masked_str = simplicity_obj.mask(case)
            logger.info('%s:\n      in: %s\n     out: %s\n S-score: %s\n',
                        desc,
                        case,
                        masked_str,
                        ''.join(['%X'%i for i in
                                 simplicity_obj.score(masked_str)
                                 ]
                                )
                        )

@cli.command()
@click.argument('window_size', default=None,
               nargs=-1)
def set_letterfreq_window(window_size):
    '''Define size of letterfreq window.
    '''
    global config_obj
    if window_size == ():
        try:
            window_size = config_obj.config_dict['letterfreq_window']
            default = ''
        except KeyError:
            window_size = DEFAULT_LETTERFREQ_WINDOW
            default = ' (default)'
        logger.info('Window size is %d residues%s',
                    window_size, default)
    elif len(window_size) > 1:
        logger.error('Only one argument for window size is permitted.')
        sys.exit(1)
    try:
        window_size = int(window_size[0])
    except ValueError:
        logger.error('Window size must be an integer value.')
        sys.exit(1)
    if window_size< 3:
        logger.error('Window size must be >=3.')
        sys.exit(1)
    config_obj.config_dict['letterfreq_window'] = window_size
    logger.info('Window size for letter-frequency simiplicity calculation is now %d residues.',
                window_size)
    config_obj.write_config_dict()