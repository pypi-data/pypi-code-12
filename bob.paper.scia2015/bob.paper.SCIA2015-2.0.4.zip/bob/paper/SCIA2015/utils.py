import bob.io.base
import bob.measure
import os

import logging
logger = logging.getLogger('bob.paper.SCIA2015')


##### Image IO ########
def save_preprocessed_images(data, data_file):
  """Saves the preprocessed data into the given data file."""
  # open file for writing
  hdf5 = bob.io.base.HDF5File(data_file, 'w')
  # write data
  hdf5.set('train_male', data['male']['world'])
  hdf5.set('train_female', data['female']['world'])
  hdf5.set('dev_male', data['male']['dev'])
  hdf5.set('dev_female', data['female']['dev'])
  if 'eval' in data['male']:
    hdf5.set('eval_male', data['male']['eval'])
    hdf5.set('eval_female', data['female']['eval'])


def get_proprocessed_images(data_file):
  """Reads the prorpocessed data from the given data file, and returns a tuple containing preprocessed images in the order:
  train_male, train_female, dev_male, dev_female, eval_male, eval_female.
  When no evaluation set is available (i.e., for the LFW database), the training set will be used both for training and development, and the development set will serve as evaluation set.
  """
  # open file for reading
  hdf5 = bob.io.base.HDF5File(data_file)
  if hdf5.has_key('eval_male'):
    # evaluation files are included (MOBIO)
    return (
      hdf5.read('train_male'),
      hdf5.read('train_female'),
      hdf5.read('dev_male'),
      hdf5.read('dev_female'),
      hdf5.read('eval_male'),
      hdf5.read('eval_female')
    )
  else:
    # no evaluation set available; use the training set as development set, and development as evalutation set
    return (
      hdf5.read('train_male'),
      hdf5.read('train_female'),
      hdf5.read('train_male'),
      hdf5.read('train_female'),
      hdf5.read('dev_male'),
      hdf5.read('dev_female')
    )

##### Evaluation of results ########
def save_results(dev_male, dev_female, eval_male, eval_female, result_file):
  """Evaluates the given score files and saves the results into the given result file."""
  # compute the threshold based on the development set
  threshold = bob.measure.eer_threshold(dev_male, dev_female)
  # compute far and frr for both development and evaluation set
  dev_far, dev_frr = bob.measure.farfrr(dev_male, dev_female, threshold)
  eval_far, eval_frr = bob.measure.farfrr(eval_male, eval_female, threshold)

  # compute classification accuracy, true positive rate (on EVAL), true negative rate (on EVAL), equal error rate (on DEV), hter (on EVAL)
  accuracy =  100*((1-eval_far)*len(eval_male) + (1-eval_frr)*len(eval_female))/(len(eval_female) + len(eval_male))
  tpr = 100*(1-eval_far)
  tnr = 100*(1-eval_frr)
  eer = (dev_far + dev_frr) / 2.
  hter = (eval_far + eval_frr) / 2.

  # store all results in the given HDF5 file
  logger.info("Writing result file '%s'" %result_file)
  bob.io.base.create_directories_safe(os.path.dirname(result_file))
  f = bob.io.base.HDF5File(result_file, 'w')
  f.set('threshold', threshold)
  f.set('dev_male_score', dev_male)
  f.set('dev_female_score', dev_female)
  f.set('eval_male_score', eval_male)
  f.set('eval_female_score', eval_female)
  f.set('accuracy', accuracy)
  f.set('tpr', tpr)
  f.set('tnr',tnr)
  f.set('eer', eer)
  f.set('hter',hter)
