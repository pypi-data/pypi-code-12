#!/usr/bin/env python

""" The script to plot the ROC curve for the MOBIO dataset. It assumes the scores using the four different algorithms have already been computed. The path of the directory containing the scores is required from the command line."""

import numpy
import os, sys
import argparse
import string
import matplotlib
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('lines', linewidth = 4)
# increase the default font size
matplotlib.rc('font', size=16)
import matplotlib.pyplot as plt

import bob.io.base

import bob.core
logger = bob.core.log.setup('bob.paper.SCIA2015')

from . import utils

def read_score_file(filename, data):
  f = bob.io.base.HDF5File(filename)
  return [f.read(d) for d in data]


def main():

  basedir = '.'
  OUTPUT_DIR = os.path.join(basedir, 'results')

  # Parse the command line arguments
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-d', '--databases', choices = ('mobio', 'lfw'), nargs='+', default=('mobio', 'lfw'), help = 'The database to preprocess.')
  parser.add_argument('-f', '--folds', nargs='+', type = int, choices = range(1,6), default = range(1,6), help = 'The folds of the LFW database to preprocess (ignored for database mobio).')
  parser.add_argument('-r', '--result-directory', metavar='DIR', default=OUTPUT_DIR, help='Base directory that will be used to save the results.')
  parser.add_argument('-t', '--result-types', nargs='+', default = ['lda', 'lbphs', 'mblbp', 'obp'], choices = ['lda', 'lbphs', 'mblbp', 'obp', 'lbp'], help = "Select the experiment types that should be evaluated")

  # initialize verbosity level
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  # collect result files
#  result_types = ['lda', 'lbphs', 'mblbp', 'obp', 'lbp']
  result_names = {'lda' : 'PCA + LDA', 'lbphs' : 'LBPHS + LDA', 'mblbp' : 'MB-LBP + Boosting', 'obp' : 'OBP + Boosting', 'lbp' : 'LBP + Boosting'}
  colors = {'lda' : 'b', 'lbphs' : 'g', 'mblbp' : 'r', 'obp' : 'm', 'lbp' : 'k'}
  markers = {'lda' : 'x', 'lbphs' : '+', 'mblbp' : 'd', 'obp' : '^', 'lbp' : 'o'}


  if 'mobio' in args.databases:

    plt.figure()
    for t in args.result_types:
      filename = os.path.join(args.result_directory, 'mobio_%s_score.hdf5'%t)
      # read files
      if os.path.exists(filename):
        logger.info("Reading result file %s" % filename)
        # get EER and HTER
        eer, hter, accuracy, tpr, tnr = read_score_file(filename, ['eer', 'hter', 'accuracy', 'tpr', 'tnr'])
#        print result_names[index], "EER = %3.2f%%, HTER = %3.2f%%, Accuracy = %3.2f%%" % (eer * 100., hter * 100., accuracy)
        print result_names[t], "Accuracy = %3.2f%%, TPR = %3.2f%%, TNR = %3.2f%%" % (accuracy, tpr, tnr)

        # collect positive and negative scores of eval set
        neg, pos = read_score_file(filename, ['eval_male_score', 'eval_female_score'])
        far, frr = bob.measure.roc(neg, pos, 200)
        plt.plot(100. * far, 100. * (1.-frr), color=colors[t], linestyle='-', marker=markers[t], markeredgewidth=2, markevery=10, linewidth=2, label=result_names[t])

    plt.xlabel('Fraction of males classified incorrectly (\%)')
    plt.ylabel('Fraction of females classified correctly (\%)')
    plt.grid(True)
    plt.legend(loc='lower right')
    plt.savefig("MOBIO.pdf")
    logger.info("Wrote MOBIO plot into MOBIO.pdf")


  if 'lfw' in args.databases:
    files = [[os.path.join(args.result_directory, 'lfw5_fold_%d_%s_score.hdf5'%(f,t)) for f in args.folds] for t in args.result_types]

    plt.figure()
    for index, t in enumerate(args.result_types):
      logger.info("Reading result files %s" % str(files[index]))
      eers = [read_score_file(files[index][f], ['eer'])[0] * 100. for f in range(len(args.folds)) if os.path.exists(files[index][f])]
      accuracies = [read_score_file(files[index][f], ['accuracy'])[0] for f in range(len(args.folds)) if os.path.exists(files[index][f])]
      tprs = [read_score_file(files[index][f], ['tpr'])[0] for f in range(len(args.folds)) if os.path.exists(files[index][f])]
      tnrs = [read_score_file(files[index][f], ['tnr'])[0] for f in range(len(args.folds)) if os.path.exists(files[index][f])]
      avg_eer = numpy.mean(eers)
      std_eer = numpy.std(eers)
      avg_acc = numpy.mean(accuracies)
#      print result_names[index], "Average EER = %3.2f%%, STD EER = %3.2f, Average Accuracy = %3.2f%%" % (avg_eer, std_eer, avg_acc)
      print result_names[t], "Accuracy = %3.2f%%, TPR = %3.2f%%, TNR = %3.2f%%" % (numpy.mean(accuracies), numpy.mean(tprs), numpy.mean(tnrs))

      # collect positive and negative scores of fold 1 set
      if os.path.exists(files[index][1]):
        neg, pos = read_score_file(files[index][1], ['eval_male_score', 'eval_female_score'])
        far, frr = bob.measure.roc(neg, pos, 200)
        plt.plot(100. * far, 100. * (1.-frr), color=colors[t], linestyle='-', marker=markers[t], markeredgewidth=2, markevery=10, linewidth=2, label=result_names[t])

    plt.xlabel('Fraction of males classified incorrectly (\%)')
    plt.ylabel('Fraction of females classified correctly (\%)')
    plt.grid(True)
    plt.legend(loc='lower right')
    plt.savefig("LFW.pdf")
    logger.info("Wrote LFW plot into LFW.pdf")
