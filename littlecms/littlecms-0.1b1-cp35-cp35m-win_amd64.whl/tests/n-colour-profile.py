#!/usr/bin/python3

""" Test for generating a simple 6-colour CMYKOG output profile.
    One B2A table is shared between the intents. The output colours from this
    table are designed to be plausible for demonstration purposes only. Simple
    algorithms are used to provide the split from Lab to CMYKOG and thus not
    modelled on a real device.
    The A2B table is the algorithmic inverse of the B2A table. The profile will
    there fore round trip accurately.
    Most of the tags are consructed manually because Little CMS doesn't provide
    support for them.
"""

from littlecms import *

# Global data
output_profile_name = r'simple_CMYKOG.icc'
device_dims = 6
device_space = cmsSig6colorData
profile_desc = "Simple CMYKOG profile\nFor demo purposes"
copyright = "No copyright, please use freely."
# Colorants + some simple encoded PCS Lab values (in range of 0-65535)
colorants = ['Cyan', 'Magenta', 'Yellow', 'Black', 'Orange', 'Green']
colorant_Lab = [ (38000, 22000, 20000), (32000, 53000, 32000), (61000, 31000, 58000),
                 (12000, 33000, 33000), (45000, 41000, 50000), (39000, 19000, 44000) ]



""" Converts a byte array to a charArray.
    Useful for cmsWriteRawTag which requires a charArray.
    tag_str may be either bytes or a str.
"""
def copy_to_charArray(tag_str):
    if isinstance(tag_str, str):
        # Convert to bytes if necessary.
        tag_str = bytes(tag_str, encoding = 'latin-1')
    tag_len = len(tag_str)
    c_str = charArray(tag_len)
    for i in range(tag_len):
        if tag_str[i] < 128:
            c_str[i] = tag_str[i]
        else:
            c_str[i] = tag_str[i] - 256
    return c_str, tag_len


""" Creates a new mediaWhitePointTag for D50.
    The tag contains an XYZNumber record with 1 element.
    A byte array is used for this tag because integers are encoded in the final string.
"""
def add_whitepoint_tag(prof):
    # Create an XYZNumber from D50
    xyz = cmsEncodedXYZNumber()
    xyz.X = int(cmsD50X * 2 ** 16)
    xyz.Y = int(cmsD50Y * 2 ** 16)
    xyz.Z = int(cmsD50Z * 2 ** 16)

    # Create the tag as a bytes array
    tag_header = b"XYZ \x00\x00\x00\x00"
    x_str = xyz.X.to_bytes(4, byteorder='big')
    y_str = xyz.Y.to_bytes(4, byteorder='big')
    z_str = xyz.Z.to_bytes(4, byteorder='big')
    tag_str = tag_header + x_str + y_str + z_str

    # Convert it to a charArray for cmsWriteRawTag
    c_str, tag_len = copy_to_charArray(tag_str)
    cmsWriteRawTag(prof, cmsSigMediaWhitePointTag, c_str, tag_len)
    del(c_str)


""" Adds a profileDescriptionTag to prof using desc_str.
    The tag contains a textDescriptionType record.
    The desc_str is copied into the ASCII element, while the unicode and scriptcode
    elements are left blank.
    A byte array is used for this tag because integers are encoded in the final string.
"""
def add_description_tag(prof, desc_str):
    # Convert desc_str to a bytes array and add a terminating null
    desc_str = bytes(desc_str, 'latin-1')
    desc_str = desc_str + b"\x00"
    # A bytes array containing the length of desc_str
    desc_len_str = len(desc_str).to_bytes(4, byteorder='big')

    # Create the tag as a bytes array
    tag_header = b"desc\x00\x00\x00\x00"
    two_byte_zero_str = b"\x00\x00"
    four_byte_zero_str = b"\x00\x00\x00\x00"
    uni_code_str = two_byte_zero_str
    uni_count_str = four_byte_zero_str
    script_code_str = two_byte_zero_str
    script_count_str = four_byte_zero_str
    script_desc = bytes(67)
    tag_str = tag_header + desc_len_str + desc_str + uni_code_str + uni_count_str + script_code_str + script_count_str + script_desc

    # Convert it to a charArray for cmsWriteRawTag
    c_str, tag_len = copy_to_charArray(tag_str)
    cmsWriteRawTag(prof, cmsSigProfileDescriptionTag, c_str, tag_len)
    del(c_str)


""" Adds a copyrightTag to prof using cprt_str.
    The tag contains a textType record.
"""
def add_copyright_tag(prof, cprt_str):
    # Create the tag as a string and add a terminating null
    tag_header = "text\x00\x00\x00\x00"
    tag_str = tag_header + cprt_str + "\x00"

    # Convert it to a charArray for cmsWriteRawTag
    c_str, tag_len = copy_to_charArray(tag_str)
    cmsWriteRawTag(prof, cmsSigCopyrightTag, c_str, tag_len)
    del(c_str)


""" Adds a colorantTableTag to prof using colorants list.
    The tag contains a colorantTableType record.
    A byte array is used for this tag because integers are encoded in the final string.
"""
def add_colorant_table_tag(prof, colorants):
    # Create the tag as a bytes array
    tag_header = b"clrt\x00\x00\x00\x00"

    count_str = len(colorants).to_bytes(4, byteorder='big')
    tag_str = tag_header + count_str

    for i in range(len(colorants)):
        clrnt = colorants[i]
        col_str = bytearray(32)
        clrnt = bytes(clrnt, encoding = 'latin-1')
        for j in range(len(clrnt)):
            col_str[j] = clrnt[j]

        # Populate pcs_str with PCS values
        pcs_str = colorant_Lab[i][0].to_bytes(2, byteorder='big') + \
                  colorant_Lab[i][1].to_bytes(2, byteorder='big') + \
                  colorant_Lab[i][2].to_bytes(2, byteorder='big')

        tag_str = tag_str + col_str + pcs_str

    # Convert it to a charArray for cmsWriteRawTag.
    c_str, tag_len = copy_to_charArray(tag_str)
    cmsWriteRawTag(prof, cmsSigColorantTableTag, c_str, tag_len)
    del(c_str)


""" Adds a BToA0Tag to prof.
    The tag is built using the pipeline tools in littlecms.
    The pipeline contains linear input and output curves, and a clut constructed
    using the b2a_clut_values() callback for each grid point.
"""
def add_b2a0_tag(ctxt, prof):
    # Make an empty B2A0 clut of the correct size
    n_grid_points = 17      # Use an odd number to map the Lab white point to a grid point
    clut_in_dims = 3        # For Lab
    clut_out_dims = device_dims
    clut = cmsStageAllocCLut16bit(ctxt, n_grid_points, clut_in_dims, clut_out_dims, None)

    # Populate the clut
    rgb = ushortArray(3)    # For efficient reuse within the sampler
    white = cmsD50_xyY()    # Set white point for D50
    Lab_profile = cmsCreateLab4Profile(white)
    sRGB_profile = cmsCreate_sRGBProfile()
    transform = cmsCreateTransform(Lab_profile, TYPE_Lab_16, sRGB_profile, TYPE_RGB_16,
                                   INTENT_RELATIVE_COLORIMETRIC, cmsFLAGS_NOCACHE)
    py_cargo = (transform, rgb)
    cmsStageSampleCLut16bit(clut, b2a_clut_values, py_cargo, 0)

    # Create a pipe container for the B2A0 clut, with identity 1d A & B curves
    b2a_pipe = cmsPipelineAlloc(ctxt, clut_in_dims, clut_out_dims)
    cmsPipelineInsertStage(b2a_pipe, cmsAT_END, clut)

    in_curves = cmsStageAllocToneCurves(ctxt, clut_in_dims, None)
    cmsPipelineInsertStage(b2a_pipe, cmsAT_BEGIN, in_curves)
    out_curves = cmsStageAllocToneCurves(ctxt, clut_out_dims, None)
    cmsPipelineInsertStage(b2a_pipe, cmsAT_END, out_curves)

    # Write the simple B2A0 tag into prof
    cmsWriteTag(prof, cmsSigBToA0Tag, b2a_pipe)

    # Tidy up
    del(rgb)
    cmsDeleteTransform(transform)
    cmsCloseProfile(Lab_profile)
    cmsCloseProfile(sRGB_profile)


""" Sampler16 callback for cmsStageSampleCLut16bit to populate the B2A clut.
    It uses a very simple method of converting to CMYKOG by first converting
    the Lab to RGB, inverting to CMY, and transfering some CMY to KOG with a
    simple method.
"""
def b2a_clut_values(in_val, out_val, py_cargo):
    one = 65535
    transform, rgb = py_cargo

    # Transform the input Lab values to sRGB
    cmsDoTransform(transform, in_val, rgb, 1)

    # Invert the sRGB to CMY
    c = one - rgb[0]
    m = one - rgb[1]
    y = one - rgb[2]

    # Transfer 50% under colour to K
    k = int(0.5 * min(c, m, y))
    c = c - k
    m = m - k
    y = y - k

    # Transfer 50% of remaining G to Green
    min_cy = min(c, y)
    green = min_cy - m
    if green > 0:
        green = int(0.5 * green)
        c = c - green
        y = y - green
    else:
        green = 0

    # Transfer 100% of remaining O to Orange
    # O is treated as Y + 0.5M
    min_my = min(m, y)
    if min_my - c > 0:          # No Orange unless C is the min of CMY
        orange = min(y-c, int(0.5 * (m-c)))
        y = y - orange
        m - m - int(0.5 * orange)
    else:
        orange = 0

    # The remainder in c/m/y is CMY
    out_val[0] = c
    out_val[1] = m
    out_val[2] = y
    out_val[3] = k
    out_val[4] = orange
    out_val[5] = green

    return True


""" Adds an AToB0Tag to prof.
    The tag is built using the pipeline tools in littlecms.
    The pipeline contains linear input and output curves, and a clut constructed
    using the a2b_clut_values() callback for each grid point.
"""
def add_a2b0_tag(ctxt, prof):
    # Make an empty B2A0 clut of the correct size
    n_grid_points = 5       # A not too high number
    clut_in_dims = device_dims
    clut_out_dims = 3       # For Lab
    clut = cmsStageAllocCLut16bit(ctxt, n_grid_points, clut_in_dims, clut_out_dims, None)

    # Populate the clut
    rgb = ushortArray(3)    # For efficient reuse within the sampler
    white = cmsD50_xyY()    # Set white point for D50
    Lab_profile = cmsCreateLab4Profile(white)
    sRGB_profile = cmsCreate_sRGBProfile()
    transform = cmsCreateTransform(sRGB_profile, TYPE_RGB_16, Lab_profile, TYPE_Lab_16,
                                  INTENT_RELATIVE_COLORIMETRIC, cmsFLAGS_NOCACHE)
    py_cargo = (transform, rgb)
    cmsStageSampleCLut16bit(clut, a2b_clut_values, py_cargo, 0)

    # Create a pipe container for the B2A0 clut, with identity 1d A & B curves
    a2b_pipe = cmsPipelineAlloc(ctxt, clut_in_dims, clut_out_dims)
    cmsPipelineInsertStage(a2b_pipe, cmsAT_END, clut)

    in_curves = cmsStageAllocToneCurves(ctxt, clut_in_dims, None)
    cmsPipelineInsertStage(a2b_pipe, cmsAT_BEGIN, in_curves)
    out_curves = cmsStageAllocToneCurves(ctxt, clut_out_dims, None)
    cmsPipelineInsertStage(a2b_pipe, cmsAT_END, out_curves)

    # Write the A2B0 tag into prof
    cmsWriteTag(prof, cmsSigAToB0Tag, a2b_pipe)

    # Tidy up
    del(rgb)
    cmsDeleteTransform(transform)
    cmsCloseProfile(Lab_profile)
    cmsCloseProfile(sRGB_profile)


""" Sampler16 callback for cmsStageSampleCLut16bit to populate the A2B clut.
    It's intended to invert the B2A0 tag as far as possible.
"""
def a2b_clut_values(in_val, out_val, py_cargo):
    one = 65535
    transform, rgb = py_cargo

    c = in_val[0]
    m = in_val[1]
    y = in_val[2]
    k = in_val[3]
    orange = in_val[4]
    green = in_val[5]

    # Transfer Orange back to MY
    y = y + orange
    m = m + int(orange * 0.5)

    # Transfer Green back to CY
    c = c + green
    y = y + green

    # Transfer K back to CMY
    c = c + k
    m = m + k
    y = y + k

    # Clip CMY if necessary
    if c > one:
        c = one
    if m > one:
        m = one
    if y > one:
        y = one

    # Invert CMY to RGB
    rgb[0] = one - c
    rgb[1] = one - m
    rgb[2] = one - y

    # Transform the nominal sRGB values to Lab
    cmsDoTransform(transform, rgb, out_val, 1)


def create_profile(save_profile):
    # Start with a simple default profile and change the header to make it 6-colour
    ctxt = cmsCreateContext(None, None)
    prof = cmsCreateProfilePlaceholder(ctxt)
    cmsSetColorSpace(prof, device_space)
    cmsSetPCS(prof, cmsSigLabData)
    cmsSetDeviceClass(prof, cmsSigOutputClass)

    # Add generic required tags
    add_whitepoint_tag(prof)
    add_description_tag(prof, profile_desc)
    add_copyright_tag(prof, copyright)

    # The N-color specific colorantsTag
    add_colorant_table_tag(prof, colorants)

    # Add the B2A tags that share one table
    add_b2a0_tag(ctxt, prof)
    cmsLinkTag(prof, cmsSigBToA1Tag, cmsSigBToA0Tag)
    cmsLinkTag(prof, cmsSigBToA2Tag, cmsSigBToA0Tag)

    # Add the A2B tags that share one table
    add_a2b0_tag(ctxt, prof)
    cmsLinkTag(prof, cmsSigAToB1Tag, cmsSigAToB0Tag)
    cmsLinkTag(prof, cmsSigAToB2Tag, cmsSigAToB0Tag)

    # Write the profile to disk with an MD5 id
    cmsMD5computeID(prof)
    if save_profile:
        cmsSaveProfileToFile(prof, output_profile_name)

    # Tidy up
    cmsCloseProfile(prof)
    cmsDeleteContext(ctxt)


if __name__ == '__main__':
    create_profile(True)

#EOF
