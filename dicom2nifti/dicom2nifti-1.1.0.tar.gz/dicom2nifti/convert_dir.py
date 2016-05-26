# -*- coding: utf-8 -*-
"""
this module houses all the code to just convert a directory of random dicom files

@author: abrys
"""
from __future__ import print_function

import gc
import os
import re
import traceback
import unicodedata

import dicom
import six
from builtins import bytes
from dicom.tag import Tag
from six import iteritems

import dicom2nifti.common as common
import dicom2nifti.convert_dicom as convert_dicom
import dicom2nifti.convert_philips as convert_philips


def convert_directory(dicom_directory, output_folder, compression=True, reorient=True):
    """
    This function will order all dicom files by series and order them one by one
    :param compression: enable or disable gzip compression
    :param reorient: reorient the dicoms according to LAS orientation
    :param output_folder: folder to write the nifti files to
    :param dicom_directory: directory with dicom files
    """
    # sort dicom files by series uid
    dicom_series = {}
    for root, _, files in os.walk(dicom_directory):
        for dicom_file in files:
            file_path = os.path.join(root, dicom_file)
            try:
                if common.is_dicom_file(file_path):
                    # read the dicom as fast as possible
                    # (max length for SeriesInstanceUID is 64 so defer_size 100 should be ok)
                    if convert_dicom.is_compressed(file_path):
                        convert_dicom.decompress_dicom(file_path)

                    dicom_headers = dicom.read_file(file_path, defer_size=100, stop_before_pixels=False)
                    if not _is_valid_imaging_dicom(dicom_headers):
                        print("Skipping: %s" % file_path)
                        continue
                    print("Organizing: %s" % file_path)
                    if dicom_headers.SeriesInstanceUID not in dicom_series:
                        dicom_series[dicom_headers.SeriesInstanceUID] = []
                    dicom_series[dicom_headers.SeriesInstanceUID].append(dicom_headers)
            except:
                print("Unable to read: %s" % file_path)
                traceback.print_exc()

    # start converting one by one
    for series_id, dicom_input in iteritems(dicom_series):
        base_filename = ""
        try:
            # construct the filename for the nifti
            base_filename = _remove_accents('%s' % dicom_input[0].SeriesNumber)
            if 'SequenceName' in dicom_input[0]:
                base_filename = _remove_accents('%s_%s' % (dicom_input[0].SeriesNumber,
                                                           dicom_input[0].SequenceName))
            elif 'ProtocolName' in dicom_input[0]:
                base_filename = _remove_accents('%s_%s' % (dicom_input[0].SeriesNumber,
                                                           dicom_input[0].ProtocolName))
            print('--------------------------------------------')
            print('Start converting ', base_filename)
            if compression:
                nifti_file = os.path.join(output_folder, base_filename + '.nii.gz')
            else:
                nifti_file = os.path.join(output_folder, base_filename + '.nii')
            convert_dicom.dicom_array_to_nifti(dicom_input, nifti_file, reorient)
            gc.collect()
        except:
            print("Unable to convert: %s" % base_filename)
            traceback.print_exc()


def _is_valid_imaging_dicom(dicom_header):
    """
    Function will do some basic checks to see if this is a valid imaging dicom
    """
    # if it is philips and multiframe dicom then we assume it is ok
    if convert_philips.is_philips([dicom_header]):
        if convert_philips.is_multiframe_dicom([dicom_header]):
            return True

    if "SeriesInstanceUID" not in dicom_header:
        return False

    if "InstanceNumber" not in dicom_header:
        return False

    # for all others if there is image position patient we assume it is ok
    if Tag(0x0020, 0x0037) not in dicom_header:
        return False

    return True


def _remove_accents(filename):
    """
    Function that will try to remove accents from a unicode string to be used in a filename.
    input filename should be either an ascii or unicode string
    """
    try:
        filename = filename.replace(" ", "_")
        if type(filename) is type(six.u('')):
            unicode_filename = filename
        else:
            unicode_filename = six.u(filename)
        cleaned_filename = unicodedata.normalize('NFKD', unicode_filename).encode('ASCII', 'ignore').decode('ASCII')

        cleaned_filename = re.sub('[^\w\s-]', '', cleaned_filename.strip().lower())
        cleaned_filename = re.sub('[-\s]+', '-', cleaned_filename)

        return cleaned_filename
    except:
        traceback.print_exc()


def _remove_accents_(filename):
    """
    Function that will try to remove accents from a unicode string to be used in a filename.
    input filename should be either an ascii or unicode string
    """
    if isinstance(filename, type(six.u(''))):
        unicode_filename = filename
    else:
        unicode_filename = six.u(filename)
    valid_characters = bytes(b'-_.() 1234567890abcdefghijklmnopqrstuvwxyz')
    cleaned_filename = unicodedata.normalize('NFKD', unicode_filename).encode('ASCII', 'ignore')

    new_filename = six.u('')

    for char_int in bytes(cleaned_filename):
        char_byte = bytes([char_int])
        if char_byte in valid_characters:
            new_filename += char_byte.decode()

    return new_filename
