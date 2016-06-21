#!/usr/bin/env python


from genonets.cmdl_handler import CmdParser  # For parsing command line arguments
from genonets.genonets_interface import Genonets  # Interface to Genonets API
from genonets.genonets_constants import AnalysisConstants as ac  # For analysis type constants


def process(args):
    gn = Genonets(args)

    gn.create()

    gn.analyze(analyses=[ac.PATHS_RATIOS])
    # gn.analyze(repertoires=["TIA1"], analyses=[ac.COVERING_IN])

    gn.saveNetResults()

    gn.saveGenotypeResults()


if __name__ == "__main__":
    # Parse the command line arguments using the Genonets command line handler, and
    # pass the list of arguments to 'process()'.
    process(CmdParser().getArgs())

    # Print message to indicate processing is done.
    print("\nDone.\n")
