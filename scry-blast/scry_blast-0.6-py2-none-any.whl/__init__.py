# The SCRY BLAST scripts are intended for use with NCBI BLAST software version 2.2.29+
# Currently supported programs are blastn, blastp, blastx, tblastn and tblastx.

__version__     = '0.2'

import options

if False:       # Have the binaries?
    pass
elif False:     # Have at least one database?
    pass
else:           # Import the procedures
    from run_blast      import RunBLAST
    from fetch_sequence import FetchSequence
