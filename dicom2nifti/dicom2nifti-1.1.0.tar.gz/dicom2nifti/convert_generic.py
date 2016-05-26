# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

from __future__ import print_function

import nibabel
import numpy
from dicom.tag import Tag

import dicom2nifti.common as common
from dicom2nifti.exceptions import ConversionError


def dicom_to_nifti(dicom_input, output_file, perform_checks=True):
    """
    This function will convert an anatomical dicom series to a nifti

    Examples: See unit test
    :param output_file: filepath to the output nifti
    :param dicom_input: directory with the dicom files for a single scan, or list of read in dicoms
    :param perform_checks: performs highly relevant consistency checks on data
    """
    if len(dicom_input) <= 0:
        raise ConversionError('NO_DICOM_FILES_FOUND')

    if perform_checks:
        # remove localizers based on image type
        dicom_input = _remove_localizers_by_imagetype(dicom_input)
        # remove_localizers based on image orientation
        dicom_input = _remove_localizers_by_orientation(dicom_input)

        # validate all the dicom files for correct orientations
        common.validate_slicecount(dicom_input)
        # validate that all slices have the same orientation
        common.validate_orientation(dicom_input)
        # validate that we have an orthogonal image (to detect gantry tilting etc)
        common.validate_orthogonal(dicom_input)

    dicom_input = sorted(dicom_input, key=lambda k: k.InstanceNumber)

    # Get data; originally z,y,x, transposed to x,y,z
    data = common.get_volume_pixeldata(dicom_input)



    affine = common.create_affine(dicom_input)

    # Convert to nifti
    img = nibabel.Nifti1Image(data, affine)

    # Set TR and TE if available
    if Tag(0x0018, 0x0081) in dicom_input[0] and Tag(0x0018, 0x0081) in dicom_input[0]:
        common.set_tr_te(img, float(dicom_input[0].RepetitionTime), float(dicom_input[0].EchoTime))

    # Save to disk
    print('Saving nifti to disk %s' % output_file)
    img.to_filename(output_file)

    return {'NII_FILE': output_file}


def _remove_localizers_by_imagetype(dicoms):
    """
    Search dicoms for localizers and delete them
    """
    # Loop overall files and build dict
    filtered_dicoms = []
    for dicom_ in dicoms:
        if 'ImageType' in dicom_ and 'LOCALIZER' in dicom_.ImageType:
            continue
        # 'Projection Image' are Localizers for CT only see MSMET-234
        if 'CT' in dicom_.Modality and 'ImageType' in dicom_ and 'PROJECTION IMAGE' in dicom_.ImageType:
            continue
        filtered_dicoms.append(dicom_)
    return filtered_dicoms


def _remove_localizers_by_orientation(dicoms):
    """
    Removing localizers based on the orientation.
    This is needed as in some cases with ct data there are some localizer/projection type images that cannot
    be distiguished by the dicom headers. This is why we kick out all orientations that do not have more than 4 files
    4 is the limit anyway for converting to nifti on our case
    """
    orientations = []
    sorted_dicoms = {}
    # Loop overall files and build dict
    for dicom_header in dicoms:
        # Create affine matrix (http://nipy.sourceforge.net/nibabel/dicom/dicom_orientation.html#dicom-slice-affine)
        image_orient1 = numpy.array(dicom_header.ImageOrientationPatient)[0:3]
        image_orient2 = numpy.array(dicom_header.ImageOrientationPatient)[3:6]
        image_orient_combined = (image_orient1.tolist(), image_orient2.tolist())
        found_orientation = False
        for orientation in orientations:
            if numpy.allclose(image_orient_combined[0], numpy.array(orientation[0]), rtol=0.001, atol=0.001) \
                    and numpy.allclose(image_orient_combined[1], numpy.array(orientation[1]), rtol=0.001,
                                       atol=0.001):
                sorted_dicoms[str(orientation)].append(dicom_header)
                found_orientation = True
                break
        if not found_orientation:
            orientations.append(image_orient_combined)
            sorted_dicoms[str(image_orient_combined)] = [dicom_header]

    # if there are multiple possible orientations delete orientations where there are less than 4 files
    # we don't convert anything less that that anyway
    filtered_dicoms = []
    for orientation in sorted_dicoms.keys():
        if len(sorted_dicoms[orientation]) > 4:
            filtered_dicoms.extend(sorted_dicoms[orientation])
    return filtered_dicoms
