#
# STIRPLATE, INC. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2016 STIRPLATE, INC., All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains
# the property of COMPANY. The intellectual and technical
# concepts contained herein are proprietary to COMPANY and
# may be covered by U.S. and Foreign Patents, patents in
# process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this
# material is strictly forbidden unless prior written permission
# is obtained from COMPANY.  Access to the source code contained
# herein is hereby forbidden to anyone except current COMPANY
# employees, managers or contractors who have executed
# Confidentiality and Non-disclosure agreements explicitly
# covering such access.
#
# The copyright notice above does not evidence any actual or
# intended publication or disclosure  of  this source code, which
# includes information that is confidential and/or proprietary,
# and is a trade secret, of  COMPANY.
#
# ANY REPRODUCTION, MODIFICATION, DISTRIBUTION, PUBLIC  PERFORMANCE,
# OR PUBLIC DISPLAY OF OR THROUGH USE  OF THIS  SOURCE CODE  WITHOUT
# THE EXPRESS WRITTEN CONSENT OF COMPANY IS STRICTLY PROHIBITED,
# AND IN VIOLATION OF APPLICABLE LAWS AND INTERNATIONAL TREATIES.
# THE RECEIPT OR POSSESSION OF  THIS SOURCE CODE AND/OR RELATED
# INFORMATION DOES NOT CONVEY OR IMPLY ANY RIGHTS TO REPRODUCE,
# DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE, USE,
# OR SELL ANYTHING THAT IT  MAY DESCRIBE, IN WHOLE OR IN PART.
#

import os
import sys
import threading
import json
import tempfile
import multiprocessing
import shutil
import datetime

# Import the required boto3 dependency.
#   Exit if it is not installed.
try:
    import boto3
    from botocore import exceptions
except ImportError, e:
    sys.stderr.write('[ERROR]: Unable to import required package boto3. Please install using: \n\n')
    sys.stderr.write('         pip install boto3\n\n')
    sys.exit(1)

try:
    import mando
except ImportError, e:
    sys.stderr.write('[ERROR]: Unable to import required package mando. Please install using: \n\n')
    sys.stderr.write('         pip install mando\n\n')
    sys.exit(1)

from collections import OrderedDict
from boto3.s3.transfer import S3Transfer, TransferConfig
from mando import main, command


class ProgressPercentage(object):
    """
    A simple progress meter for uploading to S3.

    Optional: This may be removed entirely by removing the callback
    argument in the transfer.upload_file() call below.
    """

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (self._filename, self._seen_so_far,
                                             self._size, percentage))
            sys.stdout.flush()


def upload_data(transfer, directory=None, bucket=None):
    """
    A helper script to recursively search a parent directory for sequencing data files
    to be uploaded to Stirplate automated NGS analysis platform. Processing will being
    immediately on Stirplate.io as soon as the file uploads have completed.

    To obtain a valid AWS access id and secret, please contact keith@stirplate.io,
    if one has not already been provided for you.

    :param transfer: (S3Transfer) AWS S3 transfer object.
    :param directory: (Required) The directory containing sequencing data.
    :param bucket: (Optional) The name the Stirplate-owned S3 bucket to upload to.
    """

    # Make sure we know where the files are located.
    #   Note: This will search recursively, so the 'directory'
    #   only needs to be a parent folder.
    if not directory:
        sys.exit('Please tell us where your input sequencing data are location by using the --directory keyword.')

    # Loop recursively through the parent directory and
    # upload all non-hidden files.
    uploaded = []
    for root, dirs, files in os.walk(directory):
        for f in [x for x in files if not x.startswith('.')]:
            path = os.path.join(root, f)

            try:
                # Upload! Progress will ne displayed to the STDOUT via ProgressPercentage()
                transfer.upload_file(path, bucket, f, callback=ProgressPercentage(path))
                sys.stdout.write('\n')
                uploaded.append(f)
            except exceptions.ClientError, e:
                sys.stderr.write('[ERROR]: {}\n'.format(e.message))

    # Return the list of uploaded file keys
    return uploaded


def upload_ancillary(transfer, ancillary_files=None, bucket=None):
    """
    A helper script to recursively search a parent directory for sequencing data files
    to be uploaded to Stirplate automated NGS analysis platform. Processing will being
    immediately on Stirplate.io as soon as the file uploads have completed.

    To obtain a valid AWS access id and secret, please contact keith@stirplate.io,
    if one has not already been provided for you.

    :param transfer: (S3Transfer) AWS S3 transfer object.
    :param ancillary_files: (list) A list of ancillary files to upload.
    :param bucket: (Optional) The name the Stirplate-owned S3 bucket to upload to.
    """

    # Make sure we know where the files are located.
    if not ancillary_files:
        sys.exit('Please tell us where your ancillary files are located by using the --ancillary_files keyword.')

    # Loop recursively through the parent directory and
    # upload all non-hidden files.
    uploaded = []
    for f in ancillary_files:
        try:
            # Upload! Progress will ne displayed to the STDOUT via ProgressPercentage()
            key = os.path.basename(f)
            transfer.upload_file(f, bucket, key, callback=ProgressPercentage(f))
            sys.stdout.write('\n')
            uploaded.append(os.path.basename(f))
        except exceptions.ClientError, err:
            sys.stderr.write('[ERROR]: {}\n'.format(err.message))

    # Return the list of uploaded file keys
    return uploaded


def load_credentials():
    """
    Reads the Stirplate access credentials from the
    config file (created via configure())
    """

    # Get the config file path
    path = os.path.expanduser('~/.stirplate/config')

    # Default the credentials to NoneType
    user_id = None
    key = None
    secret = None
    location = None

    # Read the config data
    if os.path.exists(path):
        with open(path, 'r') as f_h:
            config = json.load(f_h)

            # Get the credentials from the config files
            if 'access_key' in config and 'access_secret' in config:
                key = config['access_key']
                secret = config['access_secret']
                user_id = config['id']
                location = config['location']

    if all(v is None for v in [user_id, key, secret, location]):
        raise EnvironmentError('Please install your Stirplate credentials.')

    return user_id, key, secret, location


@command('rna')
def deseq(protocol='tophat',
          directory=None,
          project_name=None,
          project_description='',
          species=None,
          single_stranded_protocol=False):
    """
    Entry script for uploading RNA-seq data to Stirplate.io.

    :param protocol: (Optional) Specify the aligner to use ('tophat' or 'star') [Default: tophat].
    :param directory: (Required) Input directory containing the sequencing data.
    :param project_name: (Required) Name of the project.
    :param project_description: (Optional) Description of the project.
    :param species: (Required) Model species.
    :param single_stranded_protocol: (Optional) Single stranded protocol. [Default: False].
    """

    # Set the codes base path
    basepath = os.path.dirname(os.path.realpath(__file__))

    # Load the credentials if they are not supplied
    try:
        stirplate_id, stirplate_access_key, stirplate_access_secret, stirplate_location = load_credentials()
        sys.stdout.write('Stirplate user id: {}\n'.format(stirplate_id))
        sys.stdout.write('Stirplate access key: {}\n'.format(stirplate_access_key))
        sys.stdout.write('Stirplate access secret: {}\n'.format(
            stirplate_access_secret[-8:].rjust(len(stirplate_access_secret), "*"))
        )
        sys.stdout.write('Stirplate data location: {}\n\n'.format(stirplate_location))
    except EnvironmentError:
        sys.stderr.write('[ERROR]: Try re-configuring your connection using:\n')
        sys.stderr.write('[ERROR]:   python stirplate.py configure\n')
        sys.stderr.write('[ERROR]:      or\n')
        sys.stderr.write('[ERROR]:   python stirplate.py configure --install /path/to/stirplate/credentials.json\n\n')
        sys.exit(1)

    # Load the species data
    with open(os.path.join(basepath, 'species', 'rna.json'), 'r') as f_h:
        species_data = OrderedDict(sorted(json.load(f_h).items(), key=lambda x: x[1], reverse=True))

    try:
        # Make sure we know where the files are located.
        # Note: This will search recursively, so the 'directory' only needs to be a parent folder.
        # To specify a specific species version, please run this script with
        #    --directory <PATH_TO_DATA>
        if not directory:
            directory = raw_input('Please enter the directory of the input sequencing data: ')
            assert os.path.exists(directory), 'Could not find the input directory: {}'.format(str(directory))

        # Make sure there is a title to the project
        # To specify a title, please run this script with
        #    --project_name <PROJECT_NAME>
        if project_name is None:
            project_name = 'RNA-Seq {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # Interactively gets the users specie choice and sets the DEFAULT version.
        # To specify a specific species version, please run this script with
        #    --species <SPECIES>
        #    --species_version <SPECIES_VERSION>
        if species is None:
            # Print out the species choices
            sys.stdout.write('Please tell us what species your data is from (More available upon request):\n')
            for idx, sp in enumerate(species_data.keys()):
                sys.stdout.write('  [{}] {}\n'.format(idx + 1, sp))

            # Gets the species choice from the user
            species_selection = raw_input('Make selection [1-{}]: '.format(len(species_data)))
            species, species_version = species_data.items()[int(species_selection) - 1]
        else:
            try:
                species_version = species_data[species]
            except KeyError, species_error:
                sys.stderr.write('[ERROR]: Invalid species specfied: {}\n'.format(species_error.message))
                sys.stderr.write('[ERROR]: Please choose from: {}\n'.format(', '.join(species_data.keys())))
                sys.exit(1)

    except (AssertionError, KeyError) as err:
        sys.exit('[ERROR]: {}'.format(err.message))

    # Establish the connection to AWS, and set the transfer
    # configuration to optimize speed.
    client = boto3.client('s3', aws_access_key_id=stirplate_access_key, aws_secret_access_key=stirplate_access_secret)
    config = TransferConfig(
        multipart_threshold=8 * 1024 * 1024,
        max_concurrency=multiprocessing.cpu_count(),
        num_download_attempts=10,
    )
    transfer = S3Transfer(client, config)

    # Upload the input data
    uploaded = upload_data(transfer, directory=directory, bucket=stirplate_location)

    # Build the metadata file
    meta = {
          'user_id': stirplate_id,
          'project_name': project_name,
          'project_description': project_description,
          'protocol': protocol,
          'species': species,
          'species_version': species_version,
          'ssprotocol': 'yes' if single_stranded_protocol else 'no',
          "input_files": uploaded
    }

    # Build the metadata file (which will subsequently trigger the Stirplate processing to start)
    t = tempfile.NamedTemporaryFile(suffix='.json')
    with open(t.name, 'w') as w_h:
        json.dump(meta, w_h)

    # Upload the meta data
    try:
        transfer.upload_file(t.name, stirplate_location, os.path.basename(t.name))
    except exceptions.ClientError, e:
        sys.stderr.write('[ERROR]: {}\n'.format(e.message))
        sys.stderr.write('[ERROR]: Try re-configuring your connection using: python stirplate.py congifure\n')
    else:
        # Uploading process has completed for RNA-seq pipeline
        sys.stdout.write(('\nStirplate Processing has begun. You and your collaborators will receive an email '
                          'when the file processing has completed and analysis processing is ready to begin.\n'))


@command('gbs')
def gbs(directory=None,
        barcode_key=None,
        project_name=None,
        project_description='',
        species=None,
        species_version=None,
        restriction_enzyme=None):
    """
    Entry script for uploading Genotype-By-Sequencing (GBS) data to Stirplate.io.

    :param directory: (Required) Input directory containing the sequencing data.
    :param barcode_key: (Required) Input barcode key file containing the mapping to the sequencing data.
    :param project_name: (Required) Name of the project.
    :param project_description: (Optional) Description of the project.
    :param species: (Required) Model species.
    :param species_version: (Required) Model species annotation version.
    :param restriction_enzyme: (Required) Name of restriction enzyme used in the assay. [Dafault: None].
    """

    # Set the codes base path
    basepath = os.path.dirname(os.path.realpath(__file__))

    # Load the credentials if they are not supplied
    try:
        stirplate_id, stirplate_access_key, stirplate_access_secret, stirplate_location = load_credentials()
        sys.stdout.write('Stirplate user id: {}\n'.format(stirplate_id))
        sys.stdout.write('Stirplate access key: {}\n'.format(stirplate_access_key))
        sys.stdout.write('Stirplate access secret: {}\n'.format(
            stirplate_access_secret[-8:].rjust(len(stirplate_access_secret), "*"))
        )
        sys.stdout.write('Stirplate data location: {}\n\n'.format(stirplate_location))
    except EnvironmentError:
        sys.stderr.write('[ERROR]: Try re-configuring your connection using:\n')
        sys.stderr.write('[ERROR]:   python stirplate.py configure\n')
        sys.stderr.write('[ERROR]:      or\n')
        sys.stderr.write('[ERROR]:   python stirplate.py configure --install /path/to/stirplate/credentials.json\n\n')
        sys.exit(1)

    # Load the credentials if they are not supplied
    if stirplate_access_key is None or stirplate_access_secret is None:
        stirplate_id, stirplate_access_key, stirplate_access_secret, stirplate_location = load_credentials()

    # Set the protocol for this method
    protocol = 'gbs'

    # Load the species data
    with open(os.path.join(basepath, 'species', 'gbs.json'), 'r') as f_h:
        species_data = OrderedDict(sorted(json.load(f_h).items(), key=lambda x: x[1], reverse=True))

    # Make sure we know where the files are located.
    #   Note: This will search recursively, so the 'directory'
    #   only needs to be a parent folder.
    try:

        # Make sure the directory exists
        if not directory:
            directory = raw_input('Please enter the directory of the input sequencing data: ')
            assert os.path.exists(directory), 'Could not find the input directory: {}'.format(str(directory))

        # Make sure the barcode key file exists
        if not barcode_key:
            barcode_key = raw_input('Please enter the full path to the input barcode key file: ')
            assert os.path.exists(barcode_key), 'Could not find the input barcode key file: {}'.format(str(barcode_key))

        # Make sure there is a title to the project
        if project_name is None:
            project_name = 'GBS {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # Interactively gets the users species choice and sets the DEFAULT version.
        # To specify a specific species version, please run this script with
        #    --species <SPECIES>
        #    --species_version <SPECIES_VERSION>
        if species is None:
            # Print out the species choices
            sys.stdout.write('Please tell us what species your data is from (More available upon request):\n')
            for idx, sp in enumerate(species_data.keys()):
                sys.stdout.write('  [{}] {}\n'.format(idx + 1, sp))

            # Gets the species choice from the user
            species_selection = raw_input('Make selection [1-{}]: '.format(len(species_data)))
            species, species_version = species_data.items()[int(species_selection) - 1]
        else:
            try:
                species_version = species_data[species]
            except KeyError, s_error:
                sys.stderr.write('[ERROR]: Invalid species specfied: {}\n'.format(s_error.message))
                sys.stderr.write('[ERROR]: Please choose from: {}\n'.format(', '.join(species_data.keys())))
                sys.exit(1)

        # Interactively gets the users reastriction enzyme choice
        # To specify a specific restriction enzyme, please run this script with
        #    --restriction_enzyme <ENZYME>
        if restriction_enzyme is None:
            valid_enzymes = ['ApeKI', 'ApoI', 'BamHI', 'EcoT22I', 'HinP1I', 'HpaII', 'MseI', 'MspI',
                             'NdeI', 'PasI', 'PstI', 'Sau3AI', 'SbfI', 'AsiSI-MspI', 'BssHII-MspI',
                             'FseI-MspI', 'PaeR7I-HhaI', 'PstI-ApeKI', 'PstI-EcoT22I', 'PstI-MspI',
                             'PstI-TaqI', 'SalI-MspI', 'SbfI-MspI', ]
            for idx, ez in enumerate(valid_enzymes):
                sys.stdout.write('  [{}] {}\n'.format(idx + 1, ez))
            enzyme_input = raw_input(('Please tell us which restriction '
                                      'enzyme was used in the experiment: [1-{}]:  ').format(len(valid_enzymes)))
            try:
                restriction_enzyme = valid_enzymes[int(enzyme_input) - 1]
            except KeyError:
                sys.stdout.write('Restriction enzyme is not supported. Please select: \n')
                sys.stdout.write('  {}\n'.format(', '.join(valid_enzymes)))
                sys.exit(1)

    except (AssertionError, KeyError) as err:
        sys.exit('[ERROR]: {}'.format(err.message))

    # Establish the connection to AWS, and set the transfer
    # configuration to optimize speed.
    client = boto3.client('s3', aws_access_key_id=stirplate_access_key, aws_secret_access_key=stirplate_access_secret)
    config = TransferConfig(
        multipart_threshold=8 * 1024 * 1024,
        max_concurrency=multiprocessing.cpu_count(),
        num_download_attempts=10,
    )
    transfer = S3Transfer(client, config)

    # Upload the input data
    uploaded = upload_data(transfer, directory=directory, bucket=stirplate_location)

    # Upload the barcode file
    ancillary = upload_ancillary(transfer, ancillary_files=[barcode_key], bucket=stirplate_location)

    # Only add the data files to the input list
    for a in ancillary:
        if a in uploaded:
            uploaded.remove(a)

    # Build the metadata file
    meta = {
        'user_id': stirplate_id,
        'project_name': project_name,
        'project_description': project_description,
        'protocol': protocol,
        'species': species,
        'species_version': species_version,
        'restriction_enzyme': restriction_enzyme,
        'input_files': uploaded,
        'ancillary_files': ancillary
    }

    # Build the metadata file (which will subsequently trigger the Stirplate processing to start)
    t = tempfile.NamedTemporaryFile(suffix='.json')
    with open(t.name, 'w') as w_h:
        json.dump(meta, w_h)

    # Upload the meta data
    try:
        transfer.upload_file(t.name, stirplate_location, os.path.basename(t.name))
    except exceptions.ClientError, err:
        sys.stderr.write('[ERROR]: {}\n'.format(err.message))
        sys.stderr.write('[ERROR]: Try re-configuring your connection using: python stirplate.py configure\n')
    else:
        # Uploading process has completed for RNA-seq pipeline, DEseq protocol
        sys.stdout.write(('\nStirplate Processing has begun. You and your collaborators will receive an email '
                          'when the file processing has completed and analysis processing is ready to begin.\n'))


@command('configure')
def configure(install=None):
    """
    Sets and stores Stirplate access information
    to the local home folder.

    :param install: Path to a supplied Stirplate configurtation file.
    """

    # Verify that path is a valid config file
    config_path = os.path.expanduser('~/.stirplate/config')
    interactive = True
    if install is not None and os.path.exists(install):
        interactive = False
        with open(install, 'r') as f_h:
            data = json.load(f_h)
            for k in data.keys():
                if k not in ['access_key', 'access_secret', 'id', 'location']:
                    interactive = True

    # Obtain the user inputted information
    if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path))

    if interactive:
        stirplate_id = raw_input('Please enter the STIRPLATE USER ID: ')
        key = raw_input('Please enter the supplied STIRPLATE ACCESS ID: ')
        secret = raw_input('Please enter the supplied STIRPLATE ACCESS SECRET: ')
        location = raw_input('Please enter the supplied STIRPLATE ACCESS LOCATION: ')

        # Build the config file
        config = {
            'access_key': key,
            'access_secret': secret,
            'id': stirplate_id,
            'location': location
        }

        # Write the configuration file
        try:
            with open(config_path, 'w') as w_h:
                json.dump(config, w_h)

        except BaseException, e:
            sys.stderr.write('[ERROR]: Could not write Stirplate access file: {}\n'.format(e.message))

        else:
            sys.stdout.write('[SUCCESS]: Stirplate access file written to: {}\n'.format(config_path))

    # If info was supplied, then copy it
    else:
        shutil.copy2(install, config_path)
        sys.stdout.write('[SUCCESS]: Stirplate access file copied to: {}\n'.format(config_path))


if __name__ == '__main__':
    main()
