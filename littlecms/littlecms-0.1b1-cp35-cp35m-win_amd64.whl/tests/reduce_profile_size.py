#!/usr/bin/python3

""" Reduce the size of a CLUT profile by reducing the number of grid points

    Accept a profile as a param, and reduce the number of grid points in AToBx
    and BToAx tags.
"""

import sys
from littlecms import *

output_profile_name = r'TEST_reduced_profile.icc'
a2b_reduction_factor = 2
b2a_reduction_factor = 2


""" Creates a new textDescriptionType record as a C string.
    The desc_str is copied into the ASCII element. while the unicode and scriptcode
    elements are blank.
    Returns the C string.
"""
def create_desc_tag(desc_str):
    # Add terminating null
    desc_str = desc_str + '\x00'
    desc_len_str = len(desc_str).to_bytes(4, byteorder='big').decode()

    tag_header = 'desc\x00\x00\x00\x00'
    two_byte_zero_str = '\x00\x00'
    four_byte_zero_str = '\x00\x00\x00\x00'
    uni_code_str = two_byte_zero_str
    uni_count_str = four_byte_zero_str
    script_code_str = two_byte_zero_str
    script_count_str = four_byte_zero_str
    script_desc = bytes(67).decode()
    tag_str = tag_header + desc_len_str + desc_str + uni_code_str + uni_count_str + script_code_str + script_count_str + script_desc
    tag_len = len(tag_str)
    c_str = charArray(tag_len)
    for i in range(tag_len):
        c_str[i] = tag_str[i]
    return c_str, tag_len

""" Debug function """
def list_pipe(pipe):
    stage = cmsPipelineGetPtrToFirstStage(pipe)
    while stage:
        print(cmsStageType(stage).to_bytes(4, byteorder='big'))
        stage = cmsStageNext(stage)

""" Returns the clut stage within the pipe """
def find_clut_stage(pipe):
    stage = cmsPipelineGetPtrToFirstStage(pipe)
    while stage and cmsStageType(stage) != cmsSigCLutElemType:
        stage = cmsStageNext(stage)
    return stage

""" Sampler16 callback for cmsStageSampleCLut16bit.
    Evaluates the orig_clut using the current in_val and populates out_val with the result.
    The new values are obtained by evaluating a pipe that is set to py_cargo.
"""
def new_clut_values(in_val, out_val, py_cargo):
    pipe = py_cargo

    cmsPipelineEval16(in_val, out_val, pipe)
    return True;

""" Given a tag_sig that refers to a pipeline style tag, find the clut stage
    within the tag and reduce the number of grid points to a fraction of the
    original.
    Return a new pipeline that contains a copy of the original stages, but a
    new, reduced size, clut.
"""
def reduce_clut(ctxt, prof, tag_sig, reduce_factor):
    tag = cmsReadTag(prof, tag_sig)
    orig_pipe = void_to_pipeline(tag)
    orig_clut_stage = find_clut_stage(orig_pipe)

    # Create a tmp_pipe containing just a copy of the clut from orig_pipe
    clut_in_dims = cmsPipelineInputChannels(orig_pipe)
    clut_out_dims = cmsPipelineOutputChannels(orig_pipe)
    tmp_pipe = cmsPipelineAlloc(ctxt, clut_in_dims, clut_out_dims)
    cmsPipelineInsertStage(tmp_pipe, cmsAT_END, cmsStageDup(orig_clut_stage))

    # Obtain the number of grid points
    clut = void_to_clut_data(cmsStageData(orig_clut_stage))
    n_samples = uint32Array_frompointer(clut.Params.nSamples)

    clut_in_dims = cmsStageInputChannels(orig_clut_stage)
    clut_out_dims = cmsStageOutputChannels(orig_clut_stage)

    in_grids = uint32Array(clut_in_dims)
    for i in range(clut_in_dims):
        in_grids[i] = (n_samples[i] - 1) // reduce_factor + 1

    # Copy stages from orig_pipe to new_pipe, but substituting a new, samller, clut
    new_pipe = cmsPipelineAlloc(ctxt, clut_in_dims, clut_out_dims)
    orig_stage = cmsPipelineGetPtrToFirstStage(orig_pipe)
    while cmsStageType(orig_stage) != cmsStageType(orig_clut_stage):
        cmsPipelineInsertStage(new_pipe, cmsAT_END, cmsStageDup(orig_stage))
        orig_stage = cmsStageNext(orig_stage)
    new_clut_stage = cmsStageAllocCLut16bitGranular(ctxt, in_grids, clut_in_dims, clut_out_dims, None)
    cmsPipelineInsertStage(new_pipe, cmsAT_END, new_clut_stage)
    orig_stage = cmsStageNext(orig_stage)
    while orig_stage:
        cmsPipelineInsertStage(new_pipe, cmsAT_END, cmsStageDup(orig_stage))
        orig_stage = cmsStageNext(orig_stage)

    # py_cargo is the tmp_pipe that will be evaluated to obtain the new values
    py_cargo = tmp_pipe

    # Activate the hard work of abreviating the clut tag
    cmsStageSampleCLut16bit(new_clut_stage, new_clut_values, py_cargo, 0)
    cmsPipelineFree(tmp_pipe)

    return new_pipe


def setup(input_profile_name):
    # Start with a profile that already exists before reducing the number of grid points
    ctxt = cmsCreateContext(None, None)
    prof = cmsOpenProfileFromFile(input_profile_name, 'r')
    return ctxt, prof

def reduce_profile(ctxt, prof, save_profile):
    # The new tables will be reduced from the original colorimetric tables
    new_A2B_pipe = reduce_clut(ctxt, prof, cmsSigAToB1Tag, a2b_reduction_factor)
    new_B2A_pipe = reduce_clut(ctxt, prof, cmsSigBToA1Tag, b2a_reduction_factor)

    # Write the abreviated A2B0 tag back to the profile and reuse in other A2Bx tags
    cmsWriteTag(prof, cmsSigAToB0Tag, new_A2B_pipe)
    cmsLinkTag(prof, cmsSigAToB1Tag, cmsSigAToB0Tag)
    cmsLinkTag(prof, cmsSigAToB2Tag, cmsSigAToB0Tag)

    # Write the abreviated B2A0 tag back to the profile and reuse in other B2Ax tags
    cmsWriteTag(prof, cmsSigBToA0Tag, new_B2A_pipe)
    cmsLinkTag(prof, cmsSigBToA1Tag, cmsSigBToA0Tag)
    cmsLinkTag(prof, cmsSigBToA2Tag, cmsSigBToA0Tag)

    # Replace the profileDescriptonTag
    desc, desc_len = create_desc_tag('Reduced size profile for LittleCMS test')
    cmsWriteRawTag(prof, cmsSigProfileDescriptionTag, desc, desc_len)

    # Write the profile to disk with an MD5 id
    cmsMD5computeID(prof)
    if save_profile:
        cmsSaveProfileToFile(prof, output_profile_name)

def teardown(ctxt, prof):
    cmsCloseProfile(prof)
    cmsDeleteContext(ctxt)


if __name__ == '__main__':
    if len(sys.argv) != 2 or type(sys.argv[1]) != type(''):
        print('Error: Requires a file name as the one argument')
        exit(1)
    input_profile_name = sys.argv[1]

    ctxt, prof = setup(input_profile_name)
    reduce_profile(ctxt, prof, True)
    teardown(ctxt, prof)

#EOF
