import blessings
import clize
import os
import re
import subprocess
import sys
import tabulate

from enum import IntEnum
from inspect import getmembers
from pathlib import Path
from pkg_resources import resource_filename

from xml.etree.ElementTree import fromstring, tostring, Element, SubElement
from xml.sax.saxutils import quoteattr

try:
    from fireplace.cards import db as carddb
    from fireplace.implemented import is_implemented
    fireplace = True
except ImportError:
    fireplace = False

from hearthstone import enums


QUERY = '''
import module namespace hsq = "https://kellett.im/xq/hsq" at "hsq.xq";
hsq:evaluate(%s)
'''


term = blessings.Terminal()


def hs_query(qs):
    qs = 'import module namespace hs = "https://kellett.im/xq/hs" at "hs.xq";' + qs
    query = QUERY % quoteattr(qs)
    try:
        output = subprocess.check_output(['basex', '-q', query.encode()]).decode()
        xml = fromstring(output)
        return xml, output
    except Exception:
        raise


def rarity_colour(r, irc=False):
    c = {
        'FREE':        (7, 1),
        'COMMON':      (7, 1),
        'RARE':        (4, 12),
        'EPIC':        (5, 6),
        'LEGENDARY':   (3, 7)
    }.get(r, (7, 1))[1 if irc else 0]
    return c


def format_text(el):
    out = el.text or ''
    for child in el:
        if out and out[-1:] not in ('"',):
            out += ' '
        if child.tag == 'b':
            out += term.bold + (child.text or '') + term.normal
        else:
            out += child.text
        if child.tail[:1] not in (' ', '.', ',', ':', '"'):
            out += ' '
        out += child.tail
    return re.sub(r'\s+', ' ', out.strip())


def card_as_text(c, short=False, veryshort=False, flavour=False):
    stats_tag = race_tag = ''

    class_tag = '[%s %s, %s]' % (
        c.get('Class', 'NEUTRAL').title(),
        c.get('Type').title(),
        c.get('Set')
    )

    health = None
    if c.get('Type') == 'WEAPON':
        health = c.get('Durability', None)
    else:
        health = c.get('Health', None)

    mana = stats = ''
    if c.get('Cost') is not None:
        mana = '%s mana' % c.get('Cost')
    if c.get('Atk') is not None or health is not None:
        stats = '%s/%s' % (c.get('Atk', '?'), health or '?')
    if mana and stats:
        stats_tag = '[%s %s]' % (mana, stats)
    elif mana or stats:
        stats_tag = '[%s%s]' % (mana, stats)

    if c.get('Race') is not None:
        race_tag = '[%s]' % c.get('Race')

    def sne(s):
        if s:
            return ' ' + s
        else:
            return ''

    if veryshort:
        return '%s%s%s [%s]' % (
                term.color(rarity_colour(c.get('Rarity'))),
                c.get('Name'),
                term.normal,
                c.get('CardID')
            )
    elif short:
        return '%s%s%s [%s]%s%s%s' % (
                term.color(rarity_colour(c.get('Rarity'))),
                c.get('Name'),
                term.normal,
                c.get('CardID'),
                class_tag,
                stats_tag,
                race_tag
            )
    else:
        return '%s%s%s [%s]%s%s%s%s%s' % (
                term.color(rarity_colour(c.get('Rarity'))),
                c.get('Name'),
                term.normal,
                c.get('CardID'),
                class_tag,
                stats_tag,
                race_tag,
                sne(format_text(c.find('Text'))),
                sne(c.get('FlavorText', '') if flavour else ''),
            )


def cell_text(cell):
    cards = cell.findall('./Card')
    if cards:
        return ', '.join(card_as_text(card, short=True, veryshort=len(cards)>1) for card in cards)
    else:
        return cell.text


def main(*query, quiet: 'q' = False, flavour: 'f' = False, raw: 'r' = False):
    """
    Run an XQuery expression over the Hearthstone card data and print
    the results.

    flavour: Include flavour text in output.

    quiet: Don't print the number of results.

    raw: Print the raw XML from the query instead of interpreting it.
    """
    query = ' '.join(query)

    try:
        xml, raw_output = hs_query(query)
    except subprocess.CalledProcessError:
        sys.exit(1)

    typ = xml.get('type', 'raw')
    if raw:
        typ = 'raw'

    results = None

    if typ == 'cards':
        results = xml.findall('./Card')
        for card in results:
            print(card_as_text(card, flavour=flavour))
    elif typ == 'list':
        results = [x for x in xml.findall('./Element') if x.text is not None]
        for x in results:
            print(x.text)
    elif typ == 'table':
        results = xml.findall('./Row')
        print(tabulate.tabulate([cell_text(cell) for cell in row.findall('./Cell')] for row in results))
    elif typ == 'empty':
        if not quiet:
            print('No results', file=sys.stderr)
        sys.exit(1)
    elif raw_output:
        print(raw_output)

    if not quiet and results is not None:
        print('%d results' % len(results), file=sys.stderr)


def generate():
    """
    Build the XML input dataset.

    If Fireplace is installed, cards not implemented by Fireplace will have a
    "FireplaceMissing" tag added.
    """
    if fireplace:
        carddb.initialize()

    with open('enums.xml', 'w') as f:
        print('<?xml version="1.0"?>', file=f)
        print('<Enums>', file=f)

        for name, m in getmembers(enums, lambda x: isinstance(x, type) and issubclass(x, IntEnum) and x is not IntEnum):
            print('  <Enum name="%s">' % name, file=f)
            for k, v in m.__members__.items():
                print('    <Member name="%s" value="%r"/>' % (k, v.value), file=f)
            print('  </Enum>', file=f)

        print('</Enums>', file=f)

    with open('unimpl.xml', 'w') as f:
        print('<?xml version="1.0"?>', file=f)
        print('<Unimplemented>', file=f)

        if fireplace:
            for card in sorted(carddb):
                card = carddb[card]
                if not is_implemented(card):
                    print('<ID>%s</ID>' % card.id, file=f)

        print('</Unimplemented>', file=f)

    with open('cards.xml', 'w') as f:
        subprocess.check_call([
                'basex',
                '-i', resource_filename('hearthstone', 'CardDefs.xml'),
                'carddefs.xq'
            ], stdout=f)


def _main():
    os.chdir(str(Path(__file__).parent))
    clize.run(main, alt=generate)


if __name__ == '__main__':
    _main()
