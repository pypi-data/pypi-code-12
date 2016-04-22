import nibabel


def anonymise(identifiable_path, anonymous_path):
    # read identifiable data
    identifiable = nibabel.load(identifiable_path)
    identifiable_data = identifiable.get_data()

    # create an anonymous image with the identifiable voxels and affine
    anonymised = nibabel.Nifti1Image(identifiable_data, identifiable.affine)

    # copy header fields from the identifiable to anonymised images
    anonymised.header.set_data_dtype(identifiable.header.get_data_dtype())
    qform, qform_code = identifiable.get_qform(coded=True)
    anonymised.set_qform(qform, code=int(qform_code))
    sform, sform_code = identifiable.get_sform(coded=True)
    anonymised.set_sform(sform, code=int(sform_code))
    anonymised.header.set_xyzt_units(*identifiable.header.get_xyzt_units())
    anonymised.header.set_slope_inter(*identifiable.header.get_slope_inter())
    anonymised.header['pixdim'] = identifiable.header['pixdim']

    # save the anonymised image
    nibabel.save(anonymised, anonymous_path)
