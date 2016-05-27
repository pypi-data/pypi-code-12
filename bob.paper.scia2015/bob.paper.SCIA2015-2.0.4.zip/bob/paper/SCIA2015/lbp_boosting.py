#!/usr/bin/env python

"""This script performs gender classification using LBP-based (LBP, MB-LBP and OBP) and Look-Up Table boosting.
The results are stored as HDF5 files, which contain the accuracies and the classification scores.
"""

import os
import numpy
import argparse
import bob.ip.base
import bob.learn.boosting

import bob.core
logger = bob.core.log.setup('bob.paper.SCIA2015')

from . import utils


def get_lbp_features(images, max_block_size, overlap):
  """This function will extract LBP features in different block sizes from the given images.
  If overlap is set to True, OBP features are extracted, otherwise MB-LBP features.
  """
  # Initializations of variables
  lbps = [bob.ip.base.LBP(8, block_size = [size, size], block_overlap = [size-1, size-1] if overlap else [0,0]) for size in range(1, max_block_size+1)]

  feature_set = []
  # extract features for all images
  for image in images:
    # extract different size LBP features from image and concatenate into one feature vector
    feature = [lbp(image).flatten() for lbp in lbps]
    feature_set.append(numpy.hstack(feature))
  # return features as numpy array
  return numpy.array(feature_set)

def main():
  # Initialize the paths for images and annotation
  basedir = '.'
  INPUT_DIR = os.path.join(basedir, 'processed_images')
  OUTPUT_DIR = os.path.join(basedir, 'results')

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-d', '--databases', choices = ('mobio', 'lfw'), nargs='+', default=('mobio', 'lfw'), help = 'The database to preprocess.')
  parser.add_argument('-f', '--folds', nargs='+', type = int, choices = range(1,6), default = range(1,6), help = 'The folds of the LFW database to preprocess (ignored for database mobio).')
  parser.add_argument('-b', '--max-block-size', type = int, default = 7, help='The maximum block size to be used while computing the MB-LBP')
  parser.add_argument('-o', '--overlap-blocks', action='store_true', help='If selected, the maximum overlap is done while computing features (i.e., OBP features are extracted). Otherwise, MB-LBP without overlap are extracted.')
  parser.add_argument('-p', '--preprocessed-directory', metavar='DIR', default=INPUT_DIR, help='Directory where to read the preprocessed images from.')
  parser.add_argument('-r', '--result-directory', metavar='DIR', default=OUTPUT_DIR, help='Base directory that will be used to save the results.')

  # initialize verbosity level
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  # create output directory if not existent
  bob.io.base.create_directories_safe(args.result_directory)

  # collect the results that we will produce
  lbp_name = 'obp' if args.overlap_blocks else 'mblbp' if args.max_block_size > 1 else 'lbp'
  files = []
  if 'mobio' in args.databases:
    files.append(('mobio_images.hdf5', 'mobio_%s_score.hdf5'%lbp_name))
  if 'lfw' in args.databases:
    files.extend([('lfw_fold_%d_images.hdf5'%fold, 'lfw5_fold_%d_%s_score.hdf5'%(fold, lbp_name)) for fold in args.folds])

  # load preprocessed images
  for input_file, output_file in files:
    logger.info("Loading preprocessed image data from file %s", input_file)
    # get the data, which is in format:
    # train_male, train_female, dev_male, dev_female, eval_male, eval_female
    data = utils.get_proprocessed_images(os.path.join(args.preprocessed_directory, input_file))

    # extract features for all images
    logger.info("Extracting features")
    features = [get_lbp_features(images, args.max_block_size, args.overlap_blocks) for images in data]

    # train features by LUT boosting
    logger.info("Selecting features by LUT boosting")
    weak_trainer = bob.learn.boosting.LUTTrainer(maximum_feature_value = 256)
    boost_trainer = bob.learn.boosting.Boosting(weak_trainer = weak_trainer, loss_function = bob.learn.boosting.LogitLoss())

    # select training features and targets
    train_features = numpy.vstack(features[:2])
    train_targets = numpy.vstack([-numpy.ones([features[0].shape[0],1]), numpy.ones([features[1].shape[0],1])])

    # train a strong classifier for 800 rounds (will result in a combination of 800 weak classifiers)
    boosted_machine = boost_trainer.train(train_features, train_targets, number_of_rounds = 800)

    # compute classification scores, only on dev and eval data
    logger.info("Classifying features")
    scores = []
    for feature in features[2:]:
      predictions = numpy.ndarray(feature.shape[0])
      boosted_machine(feature, predictions)
      scores.append(predictions)

    logger.info("Evaluation")
    # for LDA, only the first dimension of the output vectors should be considered
    utils.save_results(scores[0], scores[1], scores[2], scores[3], result_file=os.path.join(args.result_directory, output_file))
