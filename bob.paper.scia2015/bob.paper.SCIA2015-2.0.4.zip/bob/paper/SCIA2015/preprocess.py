"""This script preprocesses the images from the given databases and writes the results into HDF5 files in the given directory."""

import argparse
import os
import pkg_resources

import bob.io.image
import bob.ip.base
import bob.ip.color
import bob.db.verification.filelist

import bob.core
logger = bob.core.log.setup('bob.paper.SCIA2015')

from . import utils


def read_annotation_file(filename):
  """This function reads the annotation files for the MOBIO or LFW database from the given filename.
  It returns just the eye positions, in a dictionary: {'reye' : (rey, rex), 'leye' : (ley, lex)}
  """
  with open(filename) as f:
    coordinates = f.read().rstrip().split()
    if len(coordinates) == 4:
      # MOBIO style: rex rey lex ley
      face_annotation = {
        'reye':(int(coordinates[1]), int(coordinates[0])),
        'leye':(int(coordinates[3]), int(coordinates[2]))
      }
    elif len(coordinates) == 18:
      # LFW style, average between inner and outer eye corners
      # in the order: 'reyeo', 'reyei', 'leyei', 'leyeo', 'noser', 'noset', 'nosel', 'mouthr', 'mouthl'
      lex = int(round((float(coordinates[4]) + float(coordinates[6]))/2.))
      ley = int(round((float(coordinates[5]) + float(coordinates[7]))/2.))
      rex = int(round((float(coordinates[0]) + float(coordinates[2]))/2.))
      rey = int(round((float(coordinates[1]) + float(coordinates[3]))/2.))

      face_annotation = {
        'reye': (rey, rex),
        'leye': (ley, lex)
      }
    else:
      raise ValueError("The coordinates in file %s could not be interpreted" % filename)
  return face_annotation

# The face cropper, which will align the faces to their eye locations
face_crop = bob.ip.base.FaceEyesNorm(eyes_distance=18, crop_size=(36, 36), eyes_center = (14.4, 18))

# The preprocessor that will reduce the effects of illumination
preprocessor = bob.ip.base.TanTriggs()

def preprocess(filename, annotations):
  """This function will read the image from the given filename and preprocess the image using the eye annotation to crop the face, and perform a preprocessor on the image."""
  assert 'reye' in annotations and 'leye' in annotations
  # load image
  image = bob.io.base.load(filename)
  if image.ndim == 3:
    image = bob.ip.color.rgb_to_gray(image)

  # perform face cropping
  cropped = face_crop(image, right_eye = annotations['reye'], left_eye = annotations['leye'])

  # perform preprocessing and return preprocessed image
  return preprocessor(cropped)


def preprocess_image_data(protocol_dir, image_dir, annotation_dir, data_file, image_extension = '.png', annotation_extension = '.pos', groups = ('world', 'dev', 'eval')):
  """This function preprocesses the images of the given protocol.
  It will read image files with the given ``image_extension`` from the ``image_dir``,
  annotation files with the given ``annotation_extension`` from the ``annotation_dir`` and write all files of all ``groups`` into the given ``data_file``
  """
  # get the path of the protocol, which is inside of this package
  protocol_path = pkg_resources.resource_filename('bob.paper.SCIA2015', os.path.join('protocol', protocol_dir))
  # open a database interface
  database = bob.db.verification.filelist.Database(protocol_path)

  logger.info("Loading protocol from '%s'", protocol_path)
  genders = ('male', 'female')
  images = {g : {d : [] for d in groups} for g in genders}
  # read the data
  for group in groups:
    for gender in genders:
      logger.info("Preprocessing files for gender '%s' and group '%s'", gender, group)
      # get the file lists for the current protocol and the given group
      if group == 'world':
        files = database.objects(groups = group, model_ids = gender)
      else:
        files = database.objects(groups = group, model_ids = gender, classes = 'client', purposes = 'probe')

      # preprocess data
      for file in files:
        # get image and annotation file names
        image_file = file.make_path(image_dir, image_extension)
        annotation_file = file.make_path(annotation_dir, annotation_extension)
        # preprocess image after reading the annotation file
        images[gender][group].append(preprocess(image_file, read_annotation_file(annotation_file)))

  # save image data to file
  logger.info("Writing preprocessed data to %s", data_file)
  utils.save_preprocessed_images(images, data_file)


def main():
  # Initialize the paths for images and annotation
  basedir = os.path.realpath('.')
  PREPROCESSED_DIR = os.path.join(basedir, 'processed_images')

  # Parse the command line arguments
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-d', '--database', choices = ('mobio', 'lfw'), required = True, help = 'The database to preprocess.')
  parser.add_argument('-f', '--folds', nargs='+', type = int, choices = range(1,6), default = range(1,6), help = 'The folds of the LFW database to preprocess (ignored for database mobio).')
  parser.add_argument('-p', '--preprocessed-directory', metavar = 'DIR', default = PREPROCESSED_DIR, help='Directory where to store the preprocessed images.')
  parser.add_argument('-i', '--image-directory', required = True, metavar = 'DIR', help = 'Directory, where the original images are stored')
  parser.add_argument('-a', '--annotation-directory', required = True, metavar = 'DIR', help = 'Directory, where the annotations are stored.')

  # initialize verbosity level
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  # create output directory if not existent
  bob.io.base.create_directories_safe(args.preprocessed_directory)


  # check the database
  if args.database == 'mobio':
    # preprocess MOBIO images and write them to mobio_images.hdf5
    preprocess_image_data(
        protocol_dir = 'mobio',
        image_dir = args.image_directory,
        annotation_dir = args.annotation_directory,
        data_file = os.path.join(args.preprocessed_directory, 'mobio_images.hdf5'),
        image_extension = '.png'
    )

  elif args.database == 'lfw':
    # preprocess all (desired) folds of the LFW database
    for fold in args.folds:
      # ... and write the images to lfw_fold_<fold>_images.hdf5
      preprocess_image_data(
          protocol_dir ='lfw/fold%d'%fold,
          image_dir = args.image_directory,
          annotation_dir = args.annotation_directory,
          data_file = os.path.join(args.preprocessed_directory, 'lfw_fold_%d_images.hdf5'%fold),
          image_extension = '.jpg',
          annotation_extension = '.jpg.pts',
          groups = ('world', 'dev')
      )
