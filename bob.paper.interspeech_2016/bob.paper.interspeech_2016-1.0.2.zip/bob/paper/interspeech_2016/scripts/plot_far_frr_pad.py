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

import re

import matplotlib.pyplot as mpl
import matplotlib.font_manager as fm

import bob.core
logger = bob.core.log.setup("bob.spoof.speech")



def command_line_arguments(command_line_parameters):
  """Parse the program options"""

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  OUTPUT_FILE = os.path.join(basedir, 'statistics.txt')
  
  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-t', '--score-types', required=False, nargs = '+', default=[], help = "The type of the scores, can be a set of values.")
  parser.add_argument('-p', '--parameters', required=False, nargs = '+', default=[], help = "The parameter for this type of the scores, can be a set of values.")
  
  parser.add_argument('-d', '--directory', type=str, required=True, help = "The the directory prefix with txt files that have FAR and FRR scores.")

  parser.add_argument('-o', '--out-file', type=str, default=OUTPUT_FILE, help = "The the directory to ouput the resulted plot (defaults to '%(default)s').")

  parser.add_argument('-s', '--style', required=False, type=str, help = "The plot line-style.")
  
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

#  if not os.path.exists(args.out_directory):
#    os.makedirs(args.out_directory)

  fid = open(args.out_file, "w")
  # fid.write("{\bf Feat.\ type} &  & {\bf DEV Threshold} & {\bf DEV EER (\%)}  & {\bf EVAL HTER (\%)}  \\ \hline \n")
  for score_type in args.score_types:
    for param in args.parameters:
      cur_dir = args.directory + "_" + score_type + "_" + param
      if not os.path.exists(cur_dir):
        continue
      for fn in os.listdir(cur_dir):
           if fn.endswith(".txt"):
              print (cur_dir)
              # print (fn)
              resfile = open(os.path.join(cur_dir, fn), "r")
              text = resfile.read()
              text_lines = text.splitlines()

              title = text_lines[0]
              if 'Development' in text_lines[0]:
                  title = score_type
              print("Results of " + title + ":")
              m=re.search(r"FAR = (\w+\.\w+)", text)
              far = 100.0 * float(m.group(1)) # the value in parenthesis
              m=re.search(r"FRR = (\w+\.\w+)", text)
              frr = 100.0 * float(m.group(1)) # the value in parenthesis
              m=re.search(r"threshold = (-*\w+\.\w+)", text)
              
              if not m:
                continue
              eer_thres = float(m.group(1)) # the value in parenthesis
              print ("far=%.5f, frr=%.5f, eer_thres=%.3f" % (far, frr, eer_thres))

              m=re.search(r"SFAR = (\w+\.\w+)", text)
              sfar = 100.0 * float(m.group(1)) # the value in parenthesis
              m=re.search(r"SFRR = (\w+\.\w+)", text)
              sfrr = 100.0 * float(m.group(1)) # the value in parenthesis
              m = re.search(r"attacks: a:(\w+), ad:(\w+)", text)
              type_attack = m.group(1)
              type_device = m.group(2)
              
              hter = (sfar + sfrr)*0.5
              
              print ("%s, %s: sfar=%.5f, sfrr=%.5f, hter=%.3f" % (type_attack, type_device, sfar, sfrr, hter))

              # if hter < 15.0:
                # tableline = "%s & {\\bf %s} & {\\bf %s} & {\\bf %s} & {\\bf %5.2f} & {\\bf %5.3f} & {\\bf %5.2f} & {\\bf %5.2f} & {\\bf %5.2f} \\\\ \\hline \n" % \
                #     (score_type, param, type_attack, type_device, (far+frr)*0.5, eer_thres, sfar, sfrr, hter)
                # tableline = "%s & {\\bf %s} & {\\bf %5.3f} & {\\bf %5.2f} \\\\ \\hline \n" % \
                #     (score_type, param, eer_thres, (far+frr)*0.5)
                # tableline = "%s & {\\bf %s} & {\\bf %5.3f} & {\\bf %5.2f} \\\\ \\hline \n" % \
                #     (title, param, eer_thres, (far+frr)*0.5)
              # else:
                # tableline = "%s & %s & %5.3f & %5.2f \\\\ \\hline \n" % \
                #     (score_type, param, eer_thres, (far+frr)*0.5)
              if type_attack == 'all':
                # tableline = "%s %.3f & %.5f & %.5f \\\\ \\hline \n" % \
                #     (title, eer_thres, (far+frr)*0.5, hter)
                tableline = "%s & all & all & %.3f & %.3f & %.3f \\\\ \\hline \n" % \
                            (title, sfrr, sfar, hter)
              else:
                tableline = "%s & %s & %s & %.3f & %.3f & %.3f \\\\ \\hline \n" % \
                    (title, type_attack, type_device, sfrr, sfar, hter)
              fid.write(tableline)
#      fid.write(" \hline \n")
    fid.write(" \hline \n")
#    fid.close()
#  plot_det_curves([scores_dev_attacks, scores_dev], [scores_eval_attacks, scores_eval], outname)


if __name__ == '__main__':
    main()
