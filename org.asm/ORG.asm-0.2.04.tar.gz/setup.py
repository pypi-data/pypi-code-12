#!/usr/bin/env python

import sys
import os

PACKAGE = "ORG.asm"
AUTHOR      = 'Eric Coissac'
EMAIL       = 'eric@coissac.eu'
URL         = 'metabarcoding.org/obitools3'
LICENSE     = 'CeCILL-V2'
DESCRIPTION ="A de novo assembler dedicated to organelle genome assembling"

SRC       = 'python'
CSRC      = 'src'

classifiers=['Development Status :: 3 - Alpha',
             'Environment :: Console',
             'Intended Audience :: Science/Research',
             'License :: Other/Proprietary License',
             'Operating System :: Unix',
             'Programming Language :: Python',
             'Programming Language :: Python :: 3',
             'Topic :: Scientific/Engineering :: Bio-Informatics',
             'Topic :: Utilities',
             ]


PYTHONMIN='3.4'

directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(directory,'distutils.ext'))
sys.path.append(os.path.join(directory,SRC))

print(sys.path)


VERSION=open(os.path.join(directory,'VERSION')).read().strip()


if __name__=="__main__":
    
    from obidistutils.serenity import serenity_mode

    serenity=serenity_mode(PACKAGE,VERSION)

    from obidistutils.core import setup
    from obidistutils.core import CTOOLS
    from obidistutils.core import CEXES
    from obidistutils.core import FILES
    
    CTOOLS.extend([('buildcomplement',{"sources":["src/buildcomplement.c"]}),
                   ('buildcode',{"sources":["src/buildcode.c"]}),
                   ('buildexpand8bits',{"sources":["src/buildexpand8bits.c"]})])
    
    
    # Files starting with an @ are built by the setup script 
    # according to the FILES rules
    
    CEXES.extend([('orgasmi',{"sources":["src/orgasmi.c",
                                         "src/buffer.c",
                                         "src/buildindex.c",
                                         "@code16bits.c",
                                         "@codecomp.c",
                                         "src/compsort.c",
                                         "src/debug.c",
                                         "src/decode.c",
                                         "src/encode.c",
                                         "src/fastq.c",
                                         "src/indexinput.c",
                                         "src/indexoutput.c",
                                         "src/load.c",
                                         "src/lookfor.c",
                                         "src/malloc.c",
                                         "src/fgetln.c",
                                         "src/sort.c"
                                         ]})])    
    
    FILES.extend([('codecomp.c','buildcomplement','%(prog)s > %(dest)s'),
                  ('code16bits.c','buildcode','%(prog)s > %(dest)s'),
                  ('expand8bits.c','buildexpand8bits','%(prog)s > %(dest)s')
                  ])
 
    setup(name=PACKAGE,
          description=DESCRIPTION,
          classifiers=classifiers,
          version=VERSION,
          author=AUTHOR,
          author_email=EMAIL,
          license=LICENSE,
          url=URL,
          python_src=SRC,
          sse='sse2',
          serenity=serenity,
          pythonmin=PYTHONMIN)

