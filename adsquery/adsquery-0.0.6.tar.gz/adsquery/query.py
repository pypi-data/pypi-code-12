# -*- coding: utf-8 -*-
# Python2 compat
from __future__ import unicode_literals, print_function, division
try:
    input = raw_input
except NameError: # python3
    pass

# Imports
import ads
import argparse
# from gooey import Gooey
import re
import requests
from tqdm import tqdm
import os


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# import codecs
# import sys

# UTF8Writer = codecs.getwriter('utf8')
# sys.stdout = UTF8Writer(sys.stdout)


class BuildQuery:

    def __init__(self):
        "Creates a build object query"
        self.query = dict()
        return

    def setKey(self, key, val):
        '''Set the key to val in the query'''
        if val is not None:
            self.query[key] = val

    def execute(self):
        return ads.SearchQuery(**self.query)


def createQueryParser(parser):
    parser.description = """Example:

    adsquery query --first-author Einstein relativity
    adsquery query "Gravitational wave" --year 2015
    """
    query_param = parser.add_argument_group('Query parameters')

    query_param.add_argument(metavar='query', dest='q', type=str, nargs='*',
                             help='The search query. Can be either fielded (field:value) or unfielded (value).')
    query_param.add_argument('--rows', type=int, default=10,
                             help="number of results to return.")
    query_param.add_argument('--start', type=int, default=1,
                             help="starting point for returned results (for pagination).")
    query_param.add_argument('--fl', nargs='*',
                             help="Fields list: specify the fields contained in each returned document. Value should be a comma-separated list of field names.")
    query_param.add_argument('--fq',
                             help="Filter query: filter your results using a particular field:value condition. This parameter is repeatable.")
    query_param.add_argument('--sort', type=str, nargs=2, help='Foo')

    fields = parser.add_argument_group('Fields')
    fields.add_argument('--abstract',
                        help='the abstract of the record')
    fields.add_argument('--ack',
                        help='the acknowledgements section of an article')
    fields.add_argument('--aff',
                        help='an array of the authors affiliations')
    fields.add_argument('--alternate_bibcode',
                        help='list of alternate bibcodes for a single record')
    fields.add_argument('--alternate_title',
                        help='list of alternate titles for a single record (usually if they are in multiple languages)')
    fields.add_argument('--arxiv_class',
                        help='the arXiv class the pre-print was submitted to')
    fields.add_argument('--author',
                        help='an array of the author names associated with the record')
    fields.add_argument('--bibcode',
                        help='the canonical ADS bibcode identifier for this record')
    fields.add_argument('--bibgroup',
                        help='the bibliographic groups that the bibcode has been associated with')
    fields.add_argument('--bibstem',
                        help='the abbreviated name of the journal or publication, e.g., ApJ.')
    fields.add_argument('--body',
                        help='the full text content of the article')
    fields.add_argument('--citation_count',
                        help='number of citations the item has received')
    fields.add_argument('--copyright',
                        help='the copyright applied to the article')
    fields.add_argument('--data',
                        help='the list of sources that have data related to this bibcode')
    fields.add_argument('--database',
                        help='Which database the record is associated with.')
    fields.add_argument('--doi',
                        help='the digital object identifier of the article')
    fields.add_argument('--doctype',
                        help='the type of document it is (see here for a list of doctypes)')
    fields.add_argument('--first-author',
                        help='the first author of the article')
    fields.add_argument('--grant',
                        help='the list of grant IDs and agencies noted within an article')
    fields.add_argument('--id',
                        help='a (non-persistent) unique integer for this record, used for fast look-up of a document')
    fields.add_argument('--identifier',
                        help='an array of alternative identifiers for the record. May contain alternative bibcodes, DOIs and/or arxiv ids.')
    fields.add_argument('--indexstamp',
                        help='time at which the document was (last) indexed')
    fields.add_argument('--issue',
                        help='issue the record appeared in')
    fields.add_argument('--keyword',
                        help='an array of normalized and un-normalized keyword values associated with the record')
    fields.add_argument('--lang*',
                        help='the language of the article s title')
    fields.add_argument('--orcid-pub',
                        help='ORCiD iDs supplied by publishers')
    fields.add_argument('--orcid-user',
                        help='ORCiD iDs supplied by knonwn users in the ADS')
    fields.add_argument('--orcid-other',
                        help='ORCiD iDs supplied by anonymous users in the ADS')
    fields.add_argument('--page',
                        help='starting page')
    fields.add_argument('--property',
                        help='an array of miscellaneous flags associated with the record (see here for a list of properties')
    fields.add_argument('--pub',
                        help='the canonical name of the publication the record appeared in')
    fields.add_argument('--pubdate',
                        help='publication date in the form YYYY-MM-DD (DD value will always be "00")')
    fields.add_argument('--read-count',
                        help='number of times the record has been viewed within in a 90-day windows (ads and arxiv)')
    fields.add_argument('--title',
                        help='the title of the record')
    fields.add_argument('--vizier',
                        help='the subject tags given to the article by VizieR')
    fields.add_argument('--volume',
                        help='volume the record appeared in')
    fields.add_argument('--year',
                        help='the year the article was published')


def createGetParser(parser):
    """

    """
    parser.add_argument('--bibcode',
                        help='the canonical ADS bibcode identifier for this record')
    return


def createBibParser(parser):
    """

    """
    return


def printResults(results):
    for i, res in enumerate(results):
        if len(res.author) > 2:
            authors = res.author[0] + ' et al.'
        else:
            authors = ', '.join(res.author)

        print('{c.HEADER}[{i}]: {c.OKGREEN}{year} — {c.OKBLUE}{author}{c.ENDC}, {title}'.format(
            i=i, year=res.year, title=res.title[0], author=authors, c=bcolors))


def doQuery(args):
    query = BuildQuery()
    for key in vars(args):
        if key not in ['interactive', 'func']:
            query.setKey(key, vars(args)[key])

    # get results
    results = query.execute()

    res_as_array = []

    # loop over results
    res_as_array = [res for res in results]
    printResults(res_as_array)

    if len(res_as_array) == 0:
        print('No results')
        return

    if args.interactive:
        print('')
        mask = getList('Comma separated articles to download [e.g. 1-3, 4 ]: ')
        papers = [r for i, r in enumerate(res_as_array) if i in mask]
        print('Selected:')
        printResults(papers)

        action = getInput(
            'Download [d], bibtex[b], quit[q]? ', lambda e: e.lower())

        if 'd' in action:
            print('Downloading…')
            for paper in papers:
                print('Downloading "{}"'.format(paper.title[0]))
                downloadPaper(paper)

        if 'b' in action:
            print('Bibentries…')
            bibtex = [p.bibtex for p in tqdm(papers)]
            print(''.join(bibtex))

        return papers
    else:
        return res_ar_array


def downloadPaper(paper):
    '''Download the paper.
    :arg paper
    a result given by the ads'''
    url = "http://adsabs.harvard.edu/cgi-bin/nph-data_query?bibcode={paper.bibcode}&link_type=ARTICLE".format(
        paper=paper)
    fname = '{paper.bibcode}_{author}.pdf'.format(
        paper=paper,
        author=paper.first_author.split(',')[0])
    fname = os.path.join('/home/ccc/ADS', fname)

    if not os.path.isfile(fname):
        r = requests.get(url, stream=True)

        with open(fname, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in tqdm(r.iter_content(chunk_size=1024), total=(total_length / 1024)):
                if chunk:
                    f.write(chunk)
                    f.flush()


def getInput(help_string, parse_fun):
    valid = False
    while not valid:
        try:
            ret = input(help_string)
            ret_parsed = parse_fun(ret)
            valid = True
        except ValueError:
            valid = False

    return ret_parsed


def getList(help_string):
    '''Prompt for user input and parse the result as a list.

    :param help_string
    the string to display to the user

    :return
    a list containing the input from the user
    '''
    # prompt for article to download
    dl_input = input(help_string)

    # split around commas (with blanks)
    dl_input = re.split('\s?,\s?', dl_input)
    mask = []
    regexp = re.compile('(\d+)(-(\d+))?')
    for inp in dl_input:
        match = regexp.match(inp)
        if match is None:
            print('Invalid predicate `{}`'.format(inp))
            continue

        beg, end = match.group(1, 3)
        if end is None:
            mask.append(int(beg))
        else:
            mask += range(int(beg), int(end) + 1)
    return mask


def doGet(args):
    query = BuildQuery()
    for key in vars(args):
        query.setKey(key, vars(args)[key])


def doBib(args):
    pass


def main():
    parser = argparse.ArgumentParser(description='Get papers from the ADS')
    parser.add_argument('--no-interactive', help='Deactivate interaction',
                        dest='interactive', action='store_false')
    parser.add_argument('--token', type=str,
                        help='Your ADS token. Leave empty to use the value from ~/.ads/dev_key or from the environment variable ADS_DEV_KEY.',
                        default=None)


    subparsers = parser.add_subparsers()
    query_parser = subparsers.add_parser('query', description='Query the ADS')
    createQueryParser(query_parser)
    query_parser.set_defaults(func=doQuery)

    get_parser = subparsers.add_parser(
        'get', description='Get a paper from the ADS')
    createGetParser(get_parser)
    get_parser.set_defaults(func=doGet)

    bib_parser = subparsers.add_parser(
        'bib', description='Get bib data from the ADS')
    createBibParser(bib_parser)
    bib_parser.set_defaults(func=doBib)

    args = parser.parse_args()
    if 'q' in vars(args):
        args.q = ' '.join(args.q)

    try:
        return args.func(args)
    except AttributeError: # func not in namespace
        parser.print_help()
        return

if __name__ == '__main__':
    try:
        results = main()
    except KeyboardInterrupt:
        print('Interrupted via keyboard')
        pass
