"""
CBMPy: CBCommon module
======================
PySCeS Constraint Based Modelling (http://cbmpy.sourceforge.net)
Copyright (C) 2009-2015 Brett G. Olivier, VU University Amsterdam, Amsterdam, The Netherlands

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

Author: Brett G. Olivier
Contact email: bgoli@users.sourceforge.net
Last edit: $Author: bgoli $ ($Id: CBCommon.py 346 2015-08-03 14:09:32Z bgoli $)

"""
## gets rid of "invalid variable name" info
# pylint: disable=C0103
## gets rid of "line to long" info
# pylint: disable=C0301
## use with caution: gets rid of module xxx has no member errors (run once enabled)
# pylint: disable=E1101


# preparing for Python 3 port
from __future__ import division, print_function
from __future__ import absolute_import
#from __future__ import unicode_literals

# this is a hack that needs to be streamlined a bit
#try:
    #import cStringIO as csio
#except ImportError:
    #import io as csio

chemElementDefs = None
HAVE_PYPARSING = False
try:
    from . import pyparsing
    HAVE_PYPARSING = True
except ImportError:
    try:
        print('Attempting global PyParsing import')
        import pyparsing
        HAVE_PYPARSING = True
    except ImportError:
        print('INFO please install pyparsing to enable chemical balance checking!')

if HAVE_PYPARSING:
    pp_caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pp_lowers = pp_caps.lower()
    pp_digits = "0123456789"
    pp_element = pyparsing.Word(pp_caps, pp_lowers)
    pp_integer = pyparsing.Word(pp_digits)
    pp_elementRef = pyparsing.Group(pp_element + pyparsing.Optional(pp_integer, default="1"))
    pp_chemicalFormula = pyparsing.OneOrMore(pp_elementRef)


    pp_gene_ass = pyparsing.Word(pyparsing.alphanums + '. ') | 'or' | 'OR' | 'and' | 'AND'
    pp_gene_unnester = pyparsing.nestedExpr(content=pp_gene_ass)

ptElements = ('H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S',\
              'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'G',\
              'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag',\
              'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Hf', 'Ta', 'W', 'Re', 'Os',\
              'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Rf', 'Db',\
              'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', '112', '113', '114', '115', '116', '117', '118', 'La',\
              'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Ac',\
              'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'X', 'R', 'Z')

## too crude, need to find a better logging strategy
#CBMPYLOG = csio.StringIO()
#def printl(st, scr=True, log=False):
    #"""
    #Updated print() function that also writes to a csio buffer

    #- *st* the string
    #- *prn* print to screen
    #- *log* write to log buffer

    #"""
    #global CBMPYLOG
    #if scr:
        #print(st)
    #if log:
        #try:
            #CBMPYLOG.write(st+'\n')
        #except Exception as ex:
            #print(ex)

#def flushLogToFile(fname):
    #global CBMPYLOG
    #F = file(fname, 'w')
    #CBMPYLOG.seek(0)
    #F.write(CBMPYLOG.read())
    #F.flush()
    #F.close()
    #CBMPYLOG.close()
    #CBMPYLOG = csio.StringIO()


def parseGeneAssociation(gs):
    """
    Parse a COBRA style gene association into a nested list.

     - *gs* a string containing a gene association

    """
    # gs = '(b0810) and ( b0811 ) or ( b1234.0) and(b0809)and ( b7643 )OR(b0812 )AND( b0876)'
    gl = pp_gene_unnester.parseString('('+gs+')').asList()
    gl = gl[0]

    def f(l):
        for i in range(len(l)):
            try:
                l[i] = l[i].lower().strip()
            except Exception:
                f(l[i])

    f(gl)
    print(gl)
    return gl

def checkChemFormula(cf, quiet=False):
    """
    Checks whether a string conforms to a Chemical Formula C3Br5 etc, returns True/False. Please see the SBML
    Level 3 specification and http://wikipedia.org/wiki/Hill_system for more information.

     - *cf* a string that contains a formula to check
     - *quiet* [default=False] do not print error messages

    """
    if not HAVE_PYPARSING:
        print('\nChemical Formula parser requires PyParsing!')
        return False
    try:
        R2 = [(r[0], int(r[1])) for r in pp_chemicalFormula.parseString(cf)]
    except Exception:
        if not quiet:
            print('WARNING: \"{}\" is not a valid chemical formula.'.format(cf))
        return False

    #print(R2)
    cf2 = ''
    for l_ in R2:
        if l_[0] not in ptElements:
            #print(R2)
            if not quiet:
                print('WARNING: \"{}\" is not a valid chemical formula.'.format(cf))
            return False
        else:
            cf2 += l_[0]
            if l_[1] != 1:
                cf2 += str(l_[1])

    if cf != cf2:
        if not quiet:
            print('INFO: \"{}\" check formula.'.format(cf))
        return True
    else:
        return True

def extractGeneIdsFromString(g):
    """
    Extract and return a list of gene names from a gene association string formulation

    - *g* a COBRA style gene association string

    """
    #print('\n{}'.format(g))
    g2 = g
    if 'AND' in g2 or 'and' in g2:
        g2 = g2.replace(')AND ', ') AND ').replace(')and ', ') and ')
        g2 = g2.replace(' AND(', ' AND (').replace(' and(', ' and (')
        g2 = g2.replace(')AND(', ') AND (').replace(')and(', ') and (')
    if 'OR' in g2 or 'or' in g2:
        g2 = g2.replace(')OR ', ') OR ').replace(')or ', ') or ')
        g2 = g2.replace(' OR(', ' OR (').replace(' or(', ' or (')
        g2 = g2.replace(')OR(', ') OR (').replace(')or(', ') or (')

    g2 = g2.replace(' AND ', ' and ').replace(' OR ', ' or ')
    g3 = g2.replace('(', '').replace(')', '')
    tmp = []

    if ' and ' in g3 or ' or ' in g3:
        if ' and ' and not ' or ' in g3:
            tmp = g3.split(' and ')
        elif ' or ' and not ' and ' in g3:
            tmp = g3.split(' or ')
        else:
            tmp1 = g3.split(' or ')
            tmp = []
            for s_ in tmp1:
                if ' and ' in s_:
                    tmp3 = s_.split(' and ')
                    tmp += tmp3
                else:
                    tmp += [s_]
    else:
        tmp = [g3]
    names = []
    for n_ in tmp:
        n = n_.strip()
        if n not in names:
            names.append(n)
    if names == ['']:
        names = []
    #print(names)
    return names

class ComboGen(object):
    """
    Generate sets of unique combinations

    """
    combo = None
    combo_int = None

    def __init__(self):
        self.combo = []

    def addCombination(self, data):
        self.combo.append(','.join(data))

    def uniqueCombinations(self, data, number, temp=None):
        if temp == None:
            temp = []
        if not number:
            self.addCombination(temp)
        for i in range(len(data)):
            temp.append(data[i])
            self.uniqueCombinations(data[i+1:], number-1, temp)
            temp.pop()

    def numberifyComb2Int(self):
        tmp = []
        for c in self.combo:
            tmp.append(tuple([int(c) for c in c.split(',')]))
        self.combo_int = tmp

def processSpeciesChargeChemFormulaAnnot(s, getFromName=False, overwriteChemFormula=False, overwriteCharge=False):
    """
    Disambiguate the chemical formula from either the Notes or the overloaded name

     - *s* a species object
     - *getFromName* [default=False] whether to try strip the chemical formula from the name (old COBRA style)
     - *overwriteChemFormula* [default=False]
     - *overwriteCharge* [default=False]

    """
    tempF = ''
    if overwriteChemFormula:
        tempF = s.chemFormula
        s.chemFormula = None
    key = None
    if s.chemFormula == None or s.chemFormula == '':
        if 'chemFormula' in s.annotation:
            key = 'chemFormula'
        elif 'FORMULA' in s.annotation:
            key = 'FORMULA'
        if key != None:
            s.chemFormula = s.annotation[key]

    if not checkChemFormula(s.chemFormula, quiet=True):
        if getFromName:
            try:
                n = s.getName()
                n, cf = n.rsplit('_', 1)
                if checkChemFormula(cf, quiet=True):
                    s.chemFormula = cf
                    s.setName(n)
                else:
                    s.chemFormula = ''
            except Exception:
                s.chemFormula = ''
        else:
            s.chemFormula = ''
        if overwriteChemFormula and s.chemFormula == '':
            s.chemFormula = tempF

    else:
        if key != None:
            s.annotation.pop(key)

    key2 = None
    tempC = None
    if overwriteCharge:
        tempC = s.charge
        s.charge = None
    if s.charge == None or s.charge == '':
        if 'charge' in s.annotation:
            key2 = 'charge'
        elif 'CHARGE' in s.annotation:
            key2 = 'CHARGE'
        if key2 != None:
            chrg = s.annotation[key2]
            try:
                s.charge = int(chrg)
            except ValueError:
                print('Invalid charge: {} defined for species {}'.format(chrg, s.getPid()))
                s.charge = None
                key2 = None
    if overwriteCharge and s.charge == None:
        s.charge = tempC
    if key2 != None:
        s.annotation.pop(key2)


def binHash(keys, d):
    out = []
    for k in keys:
        if k in d:
            out.append(d[k])
        else:
            out.append(True)
    return tuple(out)

def fixId(s, replace=None):
    """
    Checks a string (Sid) to see if it is a valid C style variable. first letter must be an underscore or letter,
    the rest should be alphanumeric or underscore.

    - *s* the string to test
    - *replace* [None] default is to leave out offensive character, otherwise replace with this one

    """
    s2 = ''
    if s[0].isdigit():
        s2 = '_'
        print('Illegal start character \"{}\": prefixing an underscore'.format(s[0]))
    for c in s:
        if c.isalnum() or c == '_':
            s2 += c
        elif replace != None:
            s2 += replace
            print('Replacing illegal character \"{}\": {} --> {}'.format(c, s, s2))
        else:
            print('Skipping illegal character \"{}\": {} --> {}'.format(c, s, s2))
    return s2

def checkId(s):
    """
    Checks the validity of the string to see if it conforms to a C variable. Returns true/false

    - *s* a string

    """
    cntr = 0
    for c in s:
        if cntr == 0 and c.isalpha() or c == '_':
            pass
        elif cntr > 0 and c.isalnum() or c == '_':
            pass
        else:
            print('\"{}\" is an invalid character in \"{}\"'.format(c, s))
            return False
        cntr += 1
    return True
