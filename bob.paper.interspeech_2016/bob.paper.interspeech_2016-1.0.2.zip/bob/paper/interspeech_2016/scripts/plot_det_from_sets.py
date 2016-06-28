#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Mon  7 Sep 15:19:22 CEST 2015
#
# Copyright (C) 2012-2015 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the ipyplotied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

"""This script evaluates the given score files and computes EER and Spoofing FAR with regards to 10 types of voice attacks"""

import bob.measure

import argparse
import numpy, math
import os
import os.path
import sys

import matplotlib.pyplot as mpl
import matplotlib.font_manager as fm

import bob.core
logger = bob.core.log.setup("bob.spoof.speech")



#attacks = ['replay_phone1', 'replay_phone2', 'replay_laptop', 'replay_laptop_HQ', 'speech_synthesis_logical_access', 'speech_synthesis_physical_access', 'speech_synthesis_physical_access_HQ', 'voice_conversion_logical_access', 'voice_conversion_physical_access', 'voice_conversion_physical_access_HQ']

def load_attacks_file(filename, support="all", adevice="all", recdevice="all"):
  # split in positives and negatives
  positives = []
  negatives = []

  # read four column list line by line
  for (client_id, probe_id, filename, score) in bob.measure.load.four_column(filename):
      if client_id == probe_id:
          if (support in filename or support == "all") and \
                (adevice in filename or adevice == "all") and \
                (recdevice in filename or recdevice == "all"):
              positives.append(score)
      else:
          negatives.append(score)

  return (numpy.array(negatives, numpy.float64), numpy.array(positives, numpy.float64))


def plot_det_curves(scores_real, scores_attack, thresholds, labels, title, outname):
    from matplotlib.backends.backend_pdf import PdfPages
    pdf_name = outname+'.pdf'
    pp = PdfPages(pdf_name)
    font_size = 16
    fig = mpl.figure()
    ax1 = mpl.subplot(111)

    linestyles = ['-', '--', ':', '-.']
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

    for i in range(len(scores_real)):
      if thresholds is None:
        eer_threshold = bob.measure.eer_threshold(scores_attack[i], scores_real[i])
      else:
          eer_threshold = float(thresholds[i])
      far, frr = bob.measure.farfrr(scores_attack[i], scores_real[i], eer_threshold)
      bob.measure.plot.det(scores_attack[i], scores_real[i], 100,
                            color=colors[i % len(colors)], linestyle=linestyles[i % len(linestyles)],
                            label='%s'%(labels[i]), linewidth=2)
                            # label='%s, HTER=%.2f%%'%(labels[i], (far+frr)*50), linewidth=2)
      if far < 0.0001:
        far_scaled = bob.measure.ppndf(far+0.001)
      else:
        far_scaled = bob.measure.ppndf(far)
      if frr < 0.0001:
        frr_scaled = bob.measure.ppndf(frr+0.001)
      else:
        frr_scaled = bob.measure.ppndf(frr)
      ax1.plot(far_scaled, frr_scaled, color=colors[i % len(colors)], marker='o')
      text_coords = (far_scaled+0.1, frr_scaled)
      if i % 2:
          text_coords = (far_scaled, frr_scaled+0.15)
      if thresholds is None:
        # str_name = "EER = %.2f%%"
        str_name = "%.2f%%"
      else:
        # str_name = "HTER = %.2f%%"
        str_name = "%.2f%%"
      mpl.annotate(str_name % ((far+frr)*50), xy=(far_scaled, frr_scaled),  xycoords='data', xytext=text_coords, color=colors[i % len(colors)], fontsize=font_size)

    bob.measure.plot.det_axis([0.1, 99, 0.1, 99])
    mpl.xlabel('FAR (%)', fontsize=font_size)
    mpl.ylabel('FRR (%)', fontsize=font_size)
    mpl.legend(loc='best')
    # ax1.set_title(title, fontsize=12)
    mpl.grid()
    pp.savefig()
    pp.close()



def command_line_arguments(command_line_parameters):
  """Parse the program options"""

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  OUTPUT_DIR = os.path.join(basedir, 'plots')

  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-r', '--real-files', required=True, nargs = '+', help = "The first score file (or set) of the set.")
  parser.add_argument('-a', '--attack-files', required=True, nargs = '+', help = "The second score file (or set)  of the set.")

  parser.add_argument('-l', '--labels', required=True, nargs = '+', help = "The name(s) of det curves corresponding to the score file (or set).")

  parser.add_argument('-e', '--thresholds', required=False, nargs = '+', help = "The value(s) of thersholds when computing scores for Eval sets.")

  parser.add_argument('-t', '--plot-title', required=False, type=str, default="all", help = "Title of the plot.")

  parser.add_argument('-o', '--out-directory', dest="directory", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")

  parser.add_argument('-s', '--support', required=False, type=str, default="all", help = "Type of attack.")
  parser.add_argument('-k', '--attackdevice', required=False, type=str, default="all", help = "Attack device.")


  # add verbose option
  bob.core.log.add_command_line_option(parser)

  # parse arguments
  args = parser.parse_args(command_line_parameters)

  # set verbosity level
  bob.core.log.set_verbosity_level(logger, args.verbose)

  return args


def main(command_line_parameters=None):
  """Reads score files, computes error measures and plots curves."""

  args = command_line_arguments(command_line_parameters)

  if not os.path.exists(args.directory):
    os.makedirs(args.directory)

  support=args.support
  adevice=args.attackdevice
  thresholds = None
  if args.thresholds:
      thresholds = args.thresholds

  ## Read scores ###
  print("Loading real score files")
  # take only positive values
  scores_real  = [bob.measure.load.split_four_column(real_file)[1] for real_file in args.real_files]
  print("Loading attack score files")
  scores_attack  = [load_attacks_file(attack_file, support, adevice)[1] for attack_file in args.attack_files]

  ####################
  ## Plot DET  ###
  ####################
  if thresholds is None:
    title = 'Dev set, attack "%s" and attack device "%s"' % (support, adevice)
    outname = 'det_dev_attack_%s_adevice_%s' % (support, adevice)
  else:
    title = 'Test set, attack "%s" and attack device "%s"' % (support, adevice)
    outname = 'det_test_attack_%s_adevice_%s' % (support, adevice)
  outname = os.path.join(args.directory, outname)
  plot_det_curves(scores_real, scores_attack, thresholds, args.labels, title, outname)


if __name__ == '__main__':
    main()
