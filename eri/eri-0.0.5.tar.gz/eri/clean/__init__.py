# -*- coding: utf-8 -*-

"""
Module: clean.py
Author: zlamberty
Created: 2016-01-25

Description:
    common functions for cleaning raw data (before feature engineering)

Usage:
<usage>

"""

import re as _re
import yaml as _yaml

import eri.logging as _logging
import eri.regex as _regex
import missingno as _missingno

_logger = _logging.getLogger(__name__)


try:
    import tqdm as _tqdm
    _TQDM_LOADED = True
except ImportError:
    _logger.warning('python library tqdm not installed but not required')
    _logger.info('several eri.clean features have progress bars associated with them')
    _logger.info('install tqdm via "pip install tqdm"')
    _TQDM_LOADED = False



# ----------------------------- #
#   custom errors               #
# ----------------------------- #

class CleanError(Exception):
    pass


# ----------------------------- #
#   data validation             #
# ----------------------------- #

def warn_has_nans(df, dfname='dataframe'):
    """review the relative nan-iness of a dataframe (logs information only)

    args:
        df: a pandas data frame whose nan-iness is in question
        dfname: optional name (of the dataframe); printed in logging message

    returns:
        nothing

    """
    for colname in df.columns:
        colnans = df[colname].isnull()
        if colnans.any():
            numnans = sum(colnans)
            totrows = colnans.shape[0]
            _logger.warning(
                '"{}"[{}] is {:0.2f}% nans ({} total nans)'.format(
                    dfname,
                    colname,
                    numnans / totrows * 100.,
                    numnans
                )
            )


# ----------------------------- #
#   value lookup / replacement  #
# ----------------------------- #

def yaml_alias_replace(series, enumtype, aliasYaml):
    """take a pandas series and replace values based on an enumeration type
    (e.g. team names) and alias remappings as defined in an external yaml file.

    the replacement is *not* done in place; rather, returned

    args:
        series: a pandas series obejct
        enumtype: the type of remapping to apply (this must be a key in )
        aliasYaml: the path to a yaml file which has the following format

            # yaml file example
            fruit:
                APPLE:
                    - granny smith
                    - grnsmth
                    - crab apple
                BANANA:
                    - banana
                    - banananananananana
            car:
                audi:
                    - audi
                    - audi5000
            # end example

            this function, when called with aliasYaml being the above file and
            enumtype being 'fruit', will replace values
            {granny smith, grnsmith, crab apple} with 'APPLE'

    returns:
         A series which is the same as the input 'series', but with values
         replaced as defined in 'aliasYaml' for yaml dictionary block 'enumtype'

    raises:
        eri.clean.CleanError: either the yaml file couldn't be read, or the
            enumtype is not a valid key in the parse yaml dictionary

    """
    aliases = _load_yaml_aliases(aliasYaml)
    try:
        aliases = aliases[enumtype]
    except KeyError:
        raise CleanError(
            '{} not a valid alias re-mapping in file {}'.format(aliasyaml)
        )
    return series.str.lower().replace(aliases)


def _load_yaml_aliases(aliasYaml):
    """loads the aliases found in file aliasYaml

    args:
        aliasYaml: the path to a yaml file which has the following format; see
        above for full discusion

    returns:
        dictionary of parsed yaml replacement alias dictionaries

    raises:
        eri.clean.CleanError

    """
    try:
        with open(aliasYaml, 'r') as f:
            aliases = _yaml.load(f)
    except IOError:
        raise CleanError('file {} could not be opened'.format(aliasYaml))
    except:
        raise

    # invert
    try:
        return {
            aliastype: {
                alias: mainval
                for (mainval, aliaslist) in aliasdict.items()
                for alias in aliaslist
            }
            for (aliastype, aliasdict) in aliases.items()
        }
    except AttributeError:
        err = 'yaml file {} not formatted correctly'.format(aliasYaml)
        logger.warning(err)
        logger.debug('run help(eri.clean.yaml_alias_replace) for details')
        raise CleanError(err)
    except:
        raise


# ----------------------------- #
#   key similarity              #
# ----------------------------- #

def collapsable_keys_iter(keylist, forbidden=[], progbar=True):
    """ turn a list of keys into an iterable of primary keys and keys that could
    possibly be collapsed into that one.

    args:
        keylist: a list of keys we would like to collapse
        forbidden: uncollapsable words (e.g. forbid ohio state --> ohio)
        progbar: (bool) whether or not to display a progress bar

    yields:
        pairs of (key, matches), where matches are words that are simple text
        extensions of key

    """
    keylist = sorted(set(keylist))

    if progbar and _TQDM_LOADED:
        mainiter = _tqdm.tqdm(enumerate(keylist), total=len(keylist))
    else:
        mainiter = enumerate(keylist)

    for (i, key) in mainiter:
        matches = []

        for k in keylist[i + 1:]:
            regMatch = _re.match('{} (\w+)'.format(key), k)
            plurMatch = _re.match('{}s'.format(key), k)

            if plurMatch:
                matches.append(k)
            elif regMatch:
                if not any(nc in regMatch.groups()[0] for nc in forbidden):
                    matches.append(k)
                else:
                    # this is expected behavior, don't break yet
                    pass
            else:
                break

        if matches:
            yield key, matches


def collapsable_keys(keylist, recursive=True, recDepth=0, forbidden=[],
                     progbar=True):
    """ Given an iterable of keys, build a dictionary of
    (current_key: replacement_key) pairs. The criterian for "collapsable" is
    that the current_key value matches the regex 'replacement \w+' and is the
    *only* key to do so. Note that this process must be iterative / recursive,
    because collapsing the keys at any level will change that "only one"
    criterion.

    args:
        keylist: an iterable of keys
        recursive: whether or not to recurse; that is, collapse keys and then
            collapse whatever remains after collapsing (default: True)
        recDepth: current recursion depth, only used for logging purposes
            (default: 0)
        forbidden: keys which are forbidden from being collapsed. e.g., we never
            want to declare ohio state ~ ohio, so we forbid the collapsing of
            'state' (default: [])
        progbar: whether or not to display a progress bar (useful for large
            keylists and quick snack breaks!) (default: True)

    returns:
        dictionary of {current_key: replacement_key, ...} pairs; can be used by
        a pandas dataframe df as
            df.column = df.column.replace(replacementDict)

    """
    _logger.debug(
        'collapsing keys{}'.format(
            ' (recursion depth = {})'.format(recDepth) if recDepth else ''
        )
    )
    allKeys = sorted(set(keylist))
    replKeys = {}

    kmIter = collapsable_keys_iter(
        keylist=allKeys, forbidden=forbidden, progbar=progbar
    )
    for (key, matches) in kmIter:
        sameWithSpaces = len(set(m.replace(' ', '') for m in matches)) == 1
        if sameWithSpaces:
            for m in matches:
                replKeys[m] = key
    replaced = set(replKeys.keys())
    unreplaced = set.difference(set(allKeys), replaced)

    if recursive and replaced:
        nextStepReplKeys = collapsable_keys(
            keylist=unreplaced, recursive=recursive, recDepth=recDepth + 1,
            forbidden=forbidden, progbar=progbar
        )
        for (k, v) in replKeys.items():
            replKeys[k] = nextStepReplKeys.get(v, v)
        replKeys.update(nextStepReplKeys)

    return replKeys


# ----------------------------- #
#   iterative clean columns     #
# ----------------------------- #

class CleanColname(object):
    """An incremental column name object

    Often I find myself leaving behind cleaning step breadcrumbs. For example, I
    have a column named 'raw_data'. I clean it in four passes; the end result is
    a dataframe with the folowing column names:

        raw_data, clean_data_1, clean_data_2, clean_data_3, clean_data_4

    To reduce the possibility of a fat-finger incident, and to reduce code debt,
    I propose an object which will take care of that column naming for me.

    note: the 'next' property (see below) changes the internal state. Don't use
        it until you know what you're doing!

    note: the initial state of this object is for
            current == raw
        and
            next == '{basename}_{startInt}'

    note: it is possible this is both overcomplicated and contrary to the zen of
        python (specifically: explicit is better than implicit). I trust you to
        know when it's useful and when it's dangerous ;)

    attributes:
        basecolname: (str) the base name of cleaned columns. Others will be
            '{}_{}'.format(basecolname, stageInt)
        stage: (int) the current integer stage
        next: (str) iterates the state to the next column name, returning it
        current: (str) gets the current colname state
        peak: (str) return the next state but *don't change the current state*
        raw: (str) the name of the original raw data column we subsequently clean
        final: (str) the 'final' name to use, '{basename}_final'

    """
    def __init__(self, basecolname, startInt=0, raw=None):
        """initialize CleanColname class

        args:
            basencolname: (str) the base name of cleaned columns. Others will be
                '{}_{}'.format(basecolname, stageInt).
            startInt: (int) the integer we wish to see for the first iterated
                column (default: 0)
            raw: (str) the raw column name we clean (default: None)

        """
        self.basecolname = basecolname
        self._startInt = startInt
        self._startStage = self._startInt - 1
        self.stage = self._startStage
        self.raw = raw

    @property
    def current(self):
        if self.stage == self._startStage:
            return self.raw
        else:
            return '{}_{}'.format(self.basecolname, self.stage)

    @property
    def peak(self):
        return '{}_{}'.format(self.basecolname, self.stage + 1)

    @property
    def next(self):
        self.stage += 1
        return self.current

    @property
    def final(self):
        return '{}_final'.format(self.basecolname)


# ----------------------------- #
#   namelike data               #
# ----------------------------- #

def namelike(s):
    """convert the series data s to a normalized name-like id (spaces and
    punctuation replaced or removed, etc).

    args:
        s: (pandas.Series) data to be coerced into name-like data

    returns:
        pandas Series of updated values

    raises:
        None

    """
    sOut = s.copy().str.lower()

    # replace all '_' with spaces (to deal with wikipedia-like names)
    sOut = sOut.str.replace('_', ' ')

    # drop all punctuation
    sOut = sOut.str.replace('[,;\.\-\'ʻ]*', '')

    # drop nicknames (really, wikipedia?)
    sOut = sOut.str.replace('^(.+)\".*\" ?(.+)$', '\\1\\2')

    # drop extra long spaces
    sOut = sOut.str.replace(' {2,}', ' ')

    return sOut


def namesplit(s):
    """parse out firstname, lastname, suffix into a dataframe from namelike data
    s (where namelike is determined to be like the output of the above function;
    i.e. no punctuation or bizaare spacing)

    args:
        s: (pandas.Series) namelike data

    returns:
        pandas dataframe with columns firstname, lastname, suffix

    """
    return s.str.extract(pat=_regex.NAME_REGEX, expand=False).fillna('')


# ----------------------------- #
#   nan handling and vis        #
# ----------------------------- #

def nan_vis(df):
    """just an eri-specific wrapper to the missingno function"""
    _missingno.missingno(df)
