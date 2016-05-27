#!/usr/bin/env python

"""This script to perform the gender classification using PCA on image pixels or LBPHS features and LDA as classifier.
The results are stored as HDF5 files, which contain the accuracies and the classification scores.
"""

import os
import argparse
import numpy

import bob.ip.base
import bob.learn.linear

import bob.core
logger = bob.core.log.setup('bob.paper.SCIA2015')

from . import utils

def train_pca(data, energy_ratio = 0.98):
  """Trains a PCA matrix on the given ``data`` and keeps as many dimensions as the given ratio of energy requires."""
  # train a linear machine using PCA
  pca_trainer = bob.learn.linear.PCATrainer()
  machine, eigen_values = pca_trainer.train(data)

  # calculate the cumulative energy of the eigenvalues
  cumEnergy = [sum(eigen_values[0:eigen_values.size-i]) / sum(eigen_values) for i in range(eigen_values.size+1)]

  # calculating the number of eigenvalues to keep the required energy
  numeigvalues = eigen_values.size
  for i in range(0, len(cumEnergy)-1):
    if cumEnergy[i] < energy_ratio:
      pca_subspace = len(cumEnergy) - i
      break

  # reduce the dimensionality of the LinearMachine
  machine.resize(machine.shape[0], pca_subspace) # the second parameter gives the number of kept eigenvectors/eigenvalues
  return machine


def project(data, machine):
  """Projects the given image data using the given linear machine."""
  return numpy.vstack([machine(d.flatten()) for d in data])


def train_lda(data):
  """Trains an LDA matrix on the given ``data``, which will result in a 1D output."""
  lda_trainer = bob.learn.linear.FisherLDATrainer()
  machine, _ = lda_trainer.train(data)

  # correct direction of projection if wrong, based on training data
  male_scores = project(data[0], machine)
  female_scores = project(data[1], machine)
  if (male_scores.mean() > female_scores.mean()):
    machine.weights *= -1
  return machine


def lbphs(image, lbp=bob.ip.base.LBP(8, 1., 1., uniform=True, elbp_type='regular', border_handling='wrap')):
  """Computes LBPHS features for the image using the specified LBP extractor."""
  return bob.ip.base.lbphs(image, lbp, block_size = (6,6), block_overlap = (0,0))


def extract(images, extract_lbphs):
  if extract_lbphs:
    return numpy.vstack([numpy.hstack(lbphs(i)) for i in images]).astype(numpy.float)
  else:
    return numpy.vstack([i.flatten() for i in images]).astype(numpy.float)


def main():
  # Initialize the paths for images and annotation
  basedir = '.'
  INPUT_DIR = os.path.join(basedir, 'processed_images')
  OUTPUT_DIR = os.path.join(basedir, 'results')

  # Parse the command line arguments
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-d', '--databases', choices = ('mobio', 'lfw'), nargs='+', default=('mobio', 'lfw'), help = 'The database to preprocess.')
  parser.add_argument('-f', '--folds', nargs='+', type = int, choices = range(1,6), default = range(1,6), help = 'The folds of the LFW database to preprocess (ignored for database mobio).')
  parser.add_argument('-l', '--lbphs-features', action = 'store_true', help = 'Extract LBPHS features before performing PCA and LDA')
  parser.add_argument('-p', '--preprocessed-directory', metavar='DIR', default=INPUT_DIR, help='Directory where to read the preprocessed images from.')
  parser.add_argument('-r', '--result-directory', metavar='DIR', default=OUTPUT_DIR, help='Base directory that will be used to save the results.')

  # initialize verbosity level
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  # create output directory if not existent
  bob.io.base.create_directories_safe(args.result_directory)

  # collect the results that we will produce
  result_name = 'lbphs' if args.lbphs_features else 'lda'
  files = []
  if 'mobio' in args.databases:
    files.append(('mobio_images.hdf5', 'mobio_%s_score.hdf5'%result_name))
  if 'lfw' in args.databases:
    files.extend([('lfw_fold_%d_images.hdf5'%fold, 'lfw5_fold_%d_%s_score.hdf5'%(fold, result_name)) for fold in args.folds])

  # load preprocessed images
  for input_file, output_file in files:
    logger.info("Loading preprocessed image data from file %s", input_file)
    # get the data, which is in format:
    # train_male, train_female, dev_male, dev_female, eval_male, eval_female
    data = utils.get_proprocessed_images(os.path.join(args.preprocessed_directory, input_file))

    # extract features for all images
    features = [extract(images, args.lbphs_features) for images in data]

    # Train PCA on training features of male and female data
    logger.info("Training PCA")
    pca = train_pca(numpy.vstack(features[:2]))

    # Apply PCA on all features
    logger.info("Applying PCA")
    projected = [project(feature, pca) for feature in features]

    # Train LDA on the projected training samples
    logger.info("Training LDA")
    lda = train_lda(projected[:2])

    # Apply LDA on projected data, only on dev and eval data
    logger.info("Applying LDA")
    scores = [project(data, lda) for data in projected[2:]]

    logger.info("Evaluation")
    # for LDA, only the first dimension of the output vectors should be considered
    utils.save_results(scores[0][:,0], scores[1][:,0], scores[2][:,0], scores[3][:,0], result_file=os.path.join(args.result_directory, output_file))
