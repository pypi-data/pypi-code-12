#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Sun 01 May 2016 12:02:15 CEST 



"""
This script generates all the plots of the paper

"Heterogeneous Face Recognition using Inter-Session Variability Modelling" Figures 3 and 4

Usage:
  generate_plot_results.py [<scores-dir> --verbose]
  generate_plot_results.py -h | --help
Options:
  -h --help     Show this screen.
"""

import os
import bob.core
from docopt import docopt

import logging
logger = logging.getLogger("bob.paper.CVPRW_2016")
import subprocess


def args_fig3a(cuhk_cufs_path):
  #args = ['']#FOr some reason the first argument is ignored
  args = []
  args.append("--dev-files")
  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g1024_u160/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g1024_u160/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g1024_u160/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g1024_u160/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g1024_u160/search_split5_p2s/nonorm/scores-dev")

  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g512_u160/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g512_u160/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g512_u160/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g512_u160/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g512_u160/search_split5_p2s/nonorm/scores-dev")

  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g256_u160/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g256_u160/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g256_u160/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g256_u160/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g256_u160/search_split5_p2s/nonorm/scores-dev")

  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g128_u160/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g128_u160/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g128_u160/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g128_u160/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g128_u160/search_split5_p2s/nonorm/scores-dev")

  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g64_u160/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g64_u160/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g64_u160/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g64_u160/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g64_u160/search_split5_p2s/nonorm/scores-dev")

 
  args.append("--legends") 
  args.append("1024-Gaussians")
  args.append("512-Gaussians")
  args.append("256-Gaussians")
  args.append("128-Gaussians")
  args.append("64-Gaussians")
  args.append("--report-name")
  args.append("CUFS_varying_gaussians") 
  args.append("--rr")
  args.append("--colors")
  args.append("red")
  args.append("green")
  args.append("blue")
  args.append("cyan")
  args.append("magenta")
  args.append("yellow")
  args.append("black")
  args.append("purple")
  args.append("purple")
  args.append("--legend-font-size")
  args.append("12")
  args.append("--title")
  args.append("(a)")
  args.append("--xmin")
  args.append("85")
  args.append("--xmax")
  args.append("100")

  return args


def args_fig3b(cuhk_cufs_path):
  #args = ['']#FOr some reason the first argument is ignored
  args = []
  
  args.append("--dev-files")

  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g1024_u200/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g1024_u200/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g1024_u200/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g1024_u200/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g1024_u200/search_split5_p2s/nonorm/scores-dev")

  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g1024_u160/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g1024_u160/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g1024_u160/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g1024_u160/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g1024_u160/search_split5_p2s/nonorm/scores-dev")

  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g1024_u100/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g1024_u100/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g1024_u100/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g1024_u100/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g1024_u100/search_split5_p2s/nonorm/scores-dev")

  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g1024_u50/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g1024_u50/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g1024_u50/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g1024_u50/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g1024_u50/search_split5_p2s/nonorm/scores-dev")

  args.append(cuhk_cufs_path+ "/search_split1_p2s/ISV_nofilter/g1024_u10/search_split1_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split2_p2s/ISV_nofilter/g1024_u10/search_split2_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split3_p2s/ISV_nofilter/g1024_u10/search_split3_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split4_p2s/ISV_nofilter/g1024_u10/search_split4_p2s/nonorm/scores-dev")
  args.append(cuhk_cufs_path+ "/search_split5_p2s/ISV_nofilter/g1024_u10/search_split5_p2s/nonorm/scores-dev")

  args.append("--roc")
  args.append("--legends")
  args.append("rank-200")
  args.append("rank-160")
  args.append("rank-100")
  args.append("rank-50")
  args.append("rank-10")
  args.append("--report-name")
  args.append("CUFS_varying_rankU")
  args.append("--rr")
  args.append("--colors")
  args.append("red")
  args.append("green")
  args.append("blue")
  args.append("cyan")
  args.append("magenta")
  args.append("yellow")
  args.append("black")
  args.append("--legend-font-size")
  args.append("12")
  args.append("--title")
  args.append("(b)")
  args.append("--xmin")
  args.append("90")
  args.append("--xmax")
  args.append("100")

  return args


def args_fig4a(casia_path):
  #args = ['']#FOr some reason the first argument is ignored
  args = []
  
  args.append("--dev-files")
  
  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u160/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u160/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g1024_u160/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_4/ISV_nofilter/g1024_u160/view2_4/nonorm/scores-eval")
  args.append(casia_path + "/view2_5/ISV_nofilter/g1024_u160/view2_5/nonorm/scores-eval")
  args.append(casia_path + "/view2_6/ISV_nofilter/g1024_u160/view2_6/nonorm/scores-eval")
  args.append(casia_path + "/view2_7/ISV_nofilter/g1024_u160/view2_7/nonorm/scores-eval")
  args.append(casia_path + "/view2_8/ISV_nofilter/g1024_u160/view2_8/nonorm/scores-eval")
  args.append(casia_path + "/view2_9/ISV_nofilter/g1024_u160/view2_9/nonorm/scores-eval")
  args.append(casia_path + "/view2_10/ISV_nofilter/g1024_u160/view2_10/nonorm/scores-eval")

  args.append(casia_path + "/view2_1/ISV_nofilter/g512_u160/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g512_u160/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g512_u160/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_4/ISV_nofilter/g512_u160/view2_4/nonorm/scores-eval")
  args.append(casia_path + "/view2_5/ISV_nofilter/g512_u160/view2_5/nonorm/scores-eval")
  args.append(casia_path + "/view2_6/ISV_nofilter/g512_u160/view2_6/nonorm/scores-eval")
  args.append(casia_path + "/view2_7/ISV_nofilter/g512_u160/view2_7/nonorm/scores-eval")
  args.append(casia_path + "/view2_8/ISV_nofilter/g512_u160/view2_8/nonorm/scores-eval")
  args.append(casia_path + "/view2_9/ISV_nofilter/g512_u160/view2_9/nonorm/scores-eval")
  args.append(casia_path + "/view2_10/ISV_nofilter/g512_u160/view2_10/nonorm/scores-eval")

  args.append(casia_path + "/view2_1/ISV_nofilter/g256_u160/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g256_u160/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g256_u160/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_4/ISV_nofilter/g256_u160/view2_4/nonorm/scores-eval")
  args.append(casia_path + "/view2_5/ISV_nofilter/g256_u160/view2_5/nonorm/scores-eval")
  args.append(casia_path + "/view2_6/ISV_nofilter/g256_u160/view2_6/nonorm/scores-eval")
  args.append(casia_path + "/view2_7/ISV_nofilter/g256_u160/view2_7/nonorm/scores-eval")
  args.append(casia_path + "/view2_8/ISV_nofilter/g256_u160/view2_8/nonorm/scores-eval")
  args.append(casia_path + "/view2_9/ISV_nofilter/g256_u160/view2_9/nonorm/scores-eval")
  args.append(casia_path + "/view2_10/ISV_nofilter/g256_u160/view2_10/nonorm/scores-eval")

  args.append(casia_path + "/view2_1/ISV_nofilter/g128_u160/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g128_u160/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g128_u160/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g128_u160/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_5/ISV_nofilter/g128_u160/view2_5/nonorm/scores-eval")
  args.append(casia_path + "/view2_6/ISV_nofilter/g128_u160/view2_6/nonorm/scores-eval")
  args.append(casia_path + "/view2_7/ISV_nofilter/g128_u160/view2_7/nonorm/scores-eval")
  args.append(casia_path + "/view2_8/ISV_nofilter/g128_u160/view2_8/nonorm/scores-eval")
  args.append(casia_path + "/view2_9/ISV_nofilter/g128_u160/view2_9/nonorm/scores-eval")
  args.append(casia_path + "/view2_10/ISV_nofilter/g128_u160/view2_10/nonorm/scores-eval")

  args.append(casia_path + "/view2_1/ISV_nofilter/g64_u160/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g64_u160/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g64_u160/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_4/ISV_nofilter/g64_u160/view2_4/nonorm/scores-eval")
  args.append(casia_path + "/view2_5/ISV_nofilter/g64_u160/view2_5/nonorm/scores-eval")
  args.append(casia_path + "/view2_6/ISV_nofilter/g64_u160/view2_6/nonorm/scores-eval")
  args.append(casia_path + "/view2_7/ISV_nofilter/g64_u160/view2_7/nonorm/scores-eval")
  args.append(casia_path + "/view2_8/ISV_nofilter/g64_u160/view2_8/nonorm/scores-eval")
  args.append(casia_path + "/view2_9/ISV_nofilter/g64_u160/view2_9/nonorm/scores-eval")
  args.append(casia_path + "/view2_10/ISV_nofilter/g64_u160/view2_10/nonorm/scores-eval")

  args.append("--legend-font-size")
  args.append("8")
  args.append("--legends")
  args.append("1024-Gaussians")
  args.append("512-Gaussians")
  args.append("256-Gaussians")
  args.append("128-Gaussians")
  args.append("64-Gaussians")
  args.append("--colors")
  args.append("red")
  args.append("green")
  args.append("blue")
  args.append("cyan")
  args.append("magenta")
  args.append("yellow")
  args.append("black")
  args.append("purple")
  args.append("purple")
  args.append("--roc")
  args.append("--report-name")
  args.append("report_ISV_varying_gaussians")
  args.append("--rr")
  args.append("--legend-font-size")
  args.append(" 12")
  args.append("--title")
  args.append("(a)")
  args.append("--xmin")
  args.append("55")
  args.append("--xmax")
  args.append("100")
  
  return args




def args_fig4b(casia_path):
  #args = ['']#FOr some reason the first argument is ignored
  args = []
  
  args.append("--dev-files")
  
  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u200/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u200/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g1024_u200/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_4/ISV_nofilter/g1024_u200/view2_4/nonorm/scores-eval")
  args.append(casia_path + "/view2_5/ISV_nofilter/g1024_u200/view2_5/nonorm/scores-eval")
  args.append(casia_path + "/view2_6/ISV_nofilter/g1024_u200/view2_6/nonorm/scores-eval")
  args.append(casia_path + "/view2_7/ISV_nofilter/g1024_u200/view2_7/nonorm/scores-eval")
  args.append(casia_path + "/view2_8/ISV_nofilter/g1024_u200/view2_8/nonorm/scores-eval")
  args.append(casia_path + "/view2_9/ISV_nofilter/g1024_u200/view2_9/nonorm/scores-eval")
  args.append(casia_path + "/view2_10/ISV_nofilter/g1024_u200/view2_10/nonorm/scores-eval")

  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u160/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u160/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g1024_u160/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_4/ISV_nofilter/g1024_u160/view2_4/nonorm/scores-eval")
  args.append(casia_path + "/view2_5/ISV_nofilter/g1024_u160/view2_5/nonorm/scores-eval")
  args.append(casia_path + "/view2_6/ISV_nofilter/g1024_u160/view2_6/nonorm/scores-eval")
  args.append(casia_path + "/view2_7/ISV_nofilter/g1024_u160/view2_7/nonorm/scores-eval")
  args.append(casia_path + "/view2_8/ISV_nofilter/g1024_u160/view2_8/nonorm/scores-eval")
  args.append(casia_path + "/view2_9/ISV_nofilter/g1024_u160/view2_9/nonorm/scores-eval")
  args.append(casia_path + "/view2_10/ISV_nofilter/g1024_u160/view2_10/nonorm/scores-eval")

  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u100/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u100/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g1024_u100/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_4/ISV_nofilter/g1024_u100/view2_4/nonorm/scores-eval")
  args.append(casia_path + "/view2_5/ISV_nofilter/g1024_u100/view2_5/nonorm/scores-eval")
  args.append(casia_path + "/view2_6/ISV_nofilter/g1024_u100/view2_6/nonorm/scores-eval")
  args.append(casia_path + "/view2_7/ISV_nofilter/g1024_u100/view2_7/nonorm/scores-eval")
  args.append(casia_path + "/view2_8/ISV_nofilter/g1024_u100/view2_8/nonorm/scores-eval")
  args.append(casia_path + "/view2_9/ISV_nofilter/g1024_u100/view2_9/nonorm/scores-eval")
  args.append(casia_path + "/view2_10/ISV_nofilter/g1024_u100/view2_10/nonorm/scores-eval")

  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u50/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u50/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_3/ISV_nofilter/g1024_u50/view2_3/nonorm/scores-eval")
  args.append(casia_path + "/view2_4/ISV_nofilter/g1024_u50/view2_4/nonorm/scores-eval")
  args.append(casia_path + "/view2_5/ISV_nofilter/g1024_u50/view2_5/nonorm/scores-eval")
  args.append(casia_path + "/view2_6/ISV_nofilter/g1024_u50/view2_6/nonorm/scores-eval")
  args.append(casia_path + "/view2_7/ISV_nofilter/g1024_u50/view2_7/nonorm/scores-eval")
  args.append(casia_path + "/view2_8/ISV_nofilter/g1024_u50/view2_8/nonorm/scores-eval")
  args.append(casia_path + "/view2_9/ISV_nofilter/g1024_u50/view2_9/nonorm/scores-eval")
  args.append(casia_path + "/view2_10/ISV_nofilter/g1024_u50/view2_10/nonorm/scores-eval")

  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u10/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u10/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u10/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u10/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u10/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u10/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u10/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u10/view2_2/nonorm/scores-eval")
  args.append(casia_path + "/view2_1/ISV_nofilter/g1024_u10/view2_1/nonorm/scores-eval")
  args.append(casia_path + "/view2_2/ISV_nofilter/g1024_u10/view2_2/nonorm/scores-eval")

  args.append("--legend-font-size")
  args.append("8")
  args.append("--legends")
  args.append("rank-200")  
  args.append("rank-160")
  args.append("rank-100")
  args.append("rank-50")
  args.append("rank-10")
  args.append("--colors")
  args.append("red")
  args.append("green")
  args.append("blue")
  args.append("cyan")
  args.append("magenta")
  args.append("yellow")
  args.append("black")
  args.append("purple")
  args.append("purple")
  args.append("--roc")
  args.append("--report-name")
  args.append("CASIA_varying_rankU.pdf")
  args.append("--rr")
  args.append("--legend-font-size")
  args.append("12")
  args.append("--title")
  args.append("(b)")
  args.append("--xmin")
  args.append("40")
  args.append("--xmax")
  args.append("100")
  
  return args


def main():

  args = docopt(__doc__, version='Plots generation')  

   
  scores_dir = args['<scores-dir>']
  bob.core.log.set_verbosity_level(logger,3)
  
  if(scores_dir is None):
    scores_dir = "./CVPRW_2016/"


  
  #Check if the 2 databases directories exists
  cuhk_cufs_path = os.path.join(scores_dir,"CUHK_CUFS")
  casia_path = os.path.join(scores_dir,"CBSR_NIR_VIS_2")
  if(not os.path.exists(cuhk_cufs_path)):
    raise ValueError("Directory {0} not found. Have you download the scores from <http://www.idiap.ch/resource/biometric/data/CVPRW_2016.tar.gz>?".format(cuhk_cufs_path))
  
  if(not os.path.exists(casia_path)):
    raise ValueError("Directory {0} not found. Have you download the scores from <http://www.idiap.ch/resource/biometric/data/CVPRW_2016.tar.gz>?".format(casia_path))
    
    
  logger.info("Generating Figure 3(a)")
  fig_args = args_fig3a(cuhk_cufs_path) 
  cmd = "./bin/evaluate_cufs.py"
  fig_args.insert(0,cmd)
  subprocess.call(fig_args)
  logger.info("###########################")
  

  logger.info("Generating Figure 3(b)")
  fig_args = args_fig3b(cuhk_cufs_path) 
  cmd = "./bin/evaluate_cufs.py"
  fig_args.insert(0,cmd)  
  subprocess.call(fig_args)
  logger.info("###########################")

  
  logger.info("Generating Figure 4(a)")
  fig_args = args_fig4a(casia_path) 
  cmd = "./bin/evaluate_cufs.py"
  fig_args.insert(0,cmd)  
  subprocess.call(fig_args)
  logger.info("###########################")


  logger.info("Generating Figure 4(b)")
  fig_args = args_fig4b(casia_path) 
  cmd = "./bin/evaluate_cufs.py"
  fig_args.insert(0,cmd)  
  subprocess.call(fig_args)

  

  
