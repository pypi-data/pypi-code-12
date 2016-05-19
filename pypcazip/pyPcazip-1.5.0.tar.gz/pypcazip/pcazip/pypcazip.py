#!/usr/bin/env python
'''
 The python version of pcazip!!

 Reproduces the functionality of the old fortran- and C-based versions.

 In essence its wraps a simple set of procedures provided by two modules:
       'cofasu' - trajectory file handling
       'pcz'    - PCA analysis

 Stripped down to the bare essentials, the complete procedure is:

 >>> from MDPlus.analysis.pca import pcz
 >>> from MDPlus.core import cofasu
 >>>
 >>> f = cofasu.Fasu('topology.top','trajectory.traj')
 >>> c = cofasu.Cofasu(f)
 >>> p = pcz.Pcz(c)
 >>> p.write('compressed.pcz')

 Everything else is basically analysing and sanity-checking the arguments
 given on the command line.
'''

# General python libraries import.
import os.path as op
import sys
import logging as log
import warnings
warnings.simplefilter('ignore')

import pcazip
from MDPlus.analysis.pca import pcz
from MDPlus.core.cofasu import Fasu, Cofasu
from MDPlus.libs.pdb2selection import pdb2selection
import numpy as np
from time import time
import tempfile

'''
Begin by defining the little utility function that parses trajectory
filename strings that have the "trajfile(start:stop:step)" structure.
'''

def input_parse(infile):
    if "(" in infile:
        i = infile.find("(")
        if ")" in infile[i:]:
            j = infile.find(")")
            sel = infile[i + 1:j]
            nc = sel.count(':')
            if nc == 0:
                sel = sel + '::'
            elif nc == 1:
                sel = sel + ':'
            start = sel.partition(':')[0].partition(':')[0]
            stop = sel.partition(':')[2].partition(':')[0]
            step = sel.partition(':')[2].partition(':')[2]

            if not start.isdigit():
                start = 0
            else:
                start = int(start)
            if not stop.isdigit():
                stop = None
            else:
                stop = int(stop)
            if not step.isdigit():
                step = 1
            else:
                stop = int(stop)
            
            return infile[:i], slice(start, stop, step)
        else:
            log.error('Malformed trajectory filename: {0}'.format(infile))
            sys.exit(-1)
    else:
        return infile, slice(0, None, 1)


#############################################################################
#                                                                           #
#                        PCAZIP main function (start)                       #
#                                                                           #
#############################################################################

def pcazip(args):

    # Time the complete run time
    time0start = time()

    if args.nompi:
        comm = None
        rank = 0
        size = 1
    else:
        try:
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            rank = comm.Get_rank()
            size = comm.Get_size()
        except ImportError:
            comm = None
            rank = 0
            size = 1


    if args.verbosity > 0:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
        if rank == 0:
            log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    if args.tests:
        from subprocess import call
        import os
        import tempdir
        try:
            tdir = tempfile.mkdtemp()
            log.info('Creating temporary test directory {}'.format(tdir))
            here = os.getcwd()
            os.chdir(tdir)
            call(['wget','-q','-P', tdir,
                     'https://bitbucket.org/ramonbsc/pypcazip/downloads/test150.tar.gz'])
            call(['tar', 'xf', tdir + '/test150.tar.gz', "-C", tdir])
            os.chdir(tdir + '/test')
            call(['./run_tests.sh'])
            os.chdir(here)
            if args.verbosity:
                log.info('Please explore additional testing scripts and related trajectory files as necessary at '+op.expanduser(tdir + '/test'))
            sys.exit(0)
        except:
            if (rank == 0) and args.verbosity:
                log.error('')
                log.error('Error while trying to test the correct installation of the pyPcazip suite tools!')
                log.error('')        
            sys.exit(-1)
			
            
    '''
    Input filename and topology filename are mandatory. Hence a check on
    these two parameters should be performed:
    '''
    if (not ((args.input is None) ^ (args.album is None))) or (args.topology is None):
        if rank == 0:
            log.error('')
            log.error('All or any of the mandatory command line arguments is missing. The correct usage is:')
            log.error( 'python ./pcazip.py XOR[(-i|--input <input-file>),(-a|--album) <album-file>] -t|--topology <topology-file> [optional arguments]')
            log.error('')
            log.error('Type "python ./pcazip.py -h" or "python ./pcazip.py --help" for further details.')
            log.error('')
        sys.exit(-1)

    '''
    Multiple album files OR multiple trajectory files are permitted.
    The rule is that all the trajectory files in each album must be
    compatible with a single topology file. If more than one album file
    is specified, then either there should be one topology file that is
    applicable to ALL the album files, or there should be one topology file
    specified for each album file. Similar rules operate in cases where
    multiple trajectory files are specified on the command line: either one
    topology file common to all trajectory files, or one topology file per
    trajectory file, must be given. The same rules operate (independently)
    for the selection and masking options: either there should be one
    selection/mask that applies to ALL trajectory files or albums, or there
    should be one selection/mask for each trajectory file or album.

    Let's check that these rules are being followed. First for albums:
    '''
    if args.input is None:
        na = len(args.album)
        nt = len(args.topology)
        if args.selection is None:
            ns = 1
        else:
            ns = len(args.selection)
        if args.mask is not None:
            ns = max(ns, len(args.mask))
        if nt > 1 and nt != na:
            if rank == 0:
                log.error(("Number of topology files must be one,"
                           " or equal to the number of album files."))
            sys.exit(-1)
        if ns > 1 and ns != na:
            if rank == 0:
                log.error(("Number of masks/selections must be one,"
                           " or equal to the number of album files."))
            sys.exit(-1)
    else:
        # now for trajectories:
        na = len(args.input)
        nt = len(args.topology)
        if args.selection is None:
            ns = 1
        else:
            ns = len(args.selection)
        if args.mask is not None:
            ns = max(ns, len(args.mask))
        if nt > 1 and nt != na:
            if rank == 0:
                log.error(("Number of topology files must be one, or equal"
                           " to the number of trajectory files."))
            sys.exit(-1)
        if ns > 1 and ns != na:
            if rank == 0:
                log.error(("Number of masks/selections must be one, or equal"
                           " to the number of trajectory files."))
            sys.exit(-1)
    '''
        We can now build the key data structures.
        The data structures are:

        uniStr[]:              a list of albums a[], one per topology file.
        a[]:                   a list of trajectory specifiers (each of length 4)
        traj. specifier:       [topfile, trajfile, slice, filter] where trajfile
                               is a string containing the trajectory filename,
                               topfile is the appropriate topology file, slice
                               is a string that defines which snapshots in the
                               trajectory are to be included, using the
                               conventional start:stop:step syntax that e.g.
                               numpy uses to slice arrays, and filter is the atom
                               selection string (MDAnalysis format).

    '''
    uniStr = []
    if args.input is None:
        try:
            # There are one or more album files to process. Within an album,
            # all trajectory files will share the same topology file and filter
            # specification.
            for i in range(len(args.album)):
                log.debug('Reading album file {0}'.format(i))
                # sort out the selection string:
                if args.selection == None:
                    sel = 'all'
                else:
                    if len(args.selection) == 1:
                        sel = args.selection[0]
                    else:
                        sel = args.selection[i]
                if args.mask is not None:
                    if len(args.mask) == 1:
                        sel =  pdb2selection(args.mask[0])
                    else:
                        sel =  pdb2selection(args.mask[i]) 
                # sort out the topology file string:
                if len(args.topology) == 1:
                    top = args.topology[0]
                else:
                    top = args.topology[i]

                # Files opened in text-mode
                for input_str in open(args.album[i]):
                    # Here, we should figure out whether the input_str contains
                    #  a "\n" and in that case not append a "null"-name file
                    # that would trigger an error in further processing. We
                    # should do this step before calling this function
                    # from the point where we read the single line of the album.
                    if input_str != '\n':
                        # EOLs are converted to '\n'
                        input_str = input_str.rstrip('\n')
                        l = input_parse(input_str)
                        a = [top, l[0], l[1], sel]
                        uniStr.append(a)
        except IOError as e:
            if rank == 0:
                log.error("Problems while tried to process the album file.")
                log.error(("Check whether the album file does exist and whether"
                           " its name matches the name given in input.\n"))
                log.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            sys.exit(-2)
    else:
        '''
        One or more trajectory files have ben specified by the user, rather
        than one or more album files.
        '''
        for i in range(len(args.input)):
            log.debug('Reading trajectory file {0}'.format(i))
            # sort out the selection string:
            if args.selection == None:
                sel = 'all'
            else:
                if len(args.selection) == 1:
                    sel = args.selection[0]
                else:
                    sel = args.selection[i]
            if args.mask is not None:
                if len(args.mask) == 1:
                    sel = pdb2selection(args.mask[0])
                else:
                    sel = pdb2selection(args.mask[i])
            # sort out the topology file string:
            if len(args.topology) == 1:
                top = args.topology[0]
            else:
                top = args.topology[i]

            input_str = args.input[i]
            l = input_parse(input_str)
            a = [top, l[0], l[1], sel]
            uniStr.append(a)

    # Now we can create the cofasu:
    f = []
    kwargs = {}
    if args.centre is not None:
        kwargs['centre'] = args.centre
        kwargs['pack_into_box'] = True
        if rank == 0:
            log.info('Will place group {0} at centre of box to fix jumps'.format(args.centre))
    #
    # To be nice to the user, we check if the netCDF4 module is
    # available, and if not make sure to trap attempts to load
    # AMBER .ncdf format trajectory files.
    #
    try:
        import netCDF4
        nonetCDF4 = False
    except ImportError:
        nonetCDF4 = True

    #Time reading/gathering of the trajectories in parallel
    if rank == 0:
        log.info('Reading trajectory files...')

    time1start = time()
    i = 0
    for a in uniStr:

        log.debug('Cofasu:{0} {1} {2} {3}'.format(a[0], a[1], a[2], a[3]))
        if op.splitext(a[1])[1].lower() == '.ncdf' and nonetCDF4:
            log.error('netcdf4-python with the netCDF4 and HDF5 libraries must be installed to read AMBER .ncdf files.\nSee installation instructions at https://code.google.com/p/mdanalysis/wiki/netcdf')
            exit(1)
        f.append(Fasu(a[0], a[1], frames=a[2], selection=a[3], **kwargs))
        i += 1
    try:
        cf = Cofasu(f, comm=comm)
    except(ValueError):
        if rank == 0:
            log.error('Can\'t compile trajectory files - inconsistent sizes?')
        raise
    time1end = time()

    if args.trj_output is not None:
        cf.write(args.trj_output)
        log.info('Wrote selected frames and atoms to trajectory file {0}'.format(args.trj_output))

    if args.nopca is False:
        # run the pca analysis:
        if rank == 0:
            log.info('Running pca analysis')
        # Timing the pcz-analysis with trajectories distributed across processors
        time2start = time()
        p = pcz.Pcz(cf, quality=float(args.quality), req_evecs=args.evecs,
                    version=args.file_version, fastmethod=args.fast)
        time2end = time()
        if rank == 0:
            log.info("Writing compressed trajectory")

        if args.output is not None:
            output_file = args.output
        else:
            # The input trajectory file is a mandatory argument and the check
            # on this has been done previously.
            dir = op.dirname(uniStr[0][0][1])
            base_out_compressed = op.basename(uniStr[0][0][1])
            name_out_compressed = op.splitext(base_out_compressed)[0]
            output_file = op.join(dir, name_out_compressed + "_outputPython.pcz")

        if rank == 0:
            time_write_output_0 = time()
            p.write(output_file)
            time_write_output_1 = time()

        if args.pdb_out is not None:
            cf.write(args.pdb_out, cf[0])
        if rank == 0:
            totTime = time() - time0start
            log.info('Time for reading input files: {0:.2f} s, {1:.1f}% total runtime\n'.format(time1end - time1start, (
            time1end - time1start) / totTime * 100))
            log.info('Time for pcz-analysis: {0:.2f} s, {1:.1f}% total runtime\n'.format(time2end - time2start, (
            time2end - time2start) / totTime * 100))
            log.info('Time to write the output file: {0:.2f} s, {1:.1f}% total runtime\n'.format(
                time_write_output_1 - time_write_output_0, (time_write_output_1 - time_write_output_0) / totTime * 100))
            log.info('Total run time:: {0:.2f} s\n'.format(totTime))
