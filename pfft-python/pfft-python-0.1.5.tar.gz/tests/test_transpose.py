from __future__ import absolute_import
from mpi4py import MPI

import pfft
from numpy.testing import assert_array_equal
import numpy

def main():
    comm = MPI.COMM_WORLD
    # this must run with comm.size == 3
    assert comm.size == 1
    # first do a fft with transposed in

    in1 = numpy.zeros((4,  3), dtype='complex64')
    in1[..., 1] = numpy.arange(4) * 1j
    print in1
    out = dofft(in1, pfft.Type.PFFT_C2R, pfft.Flags.PFFT_TRANSPOSED_IN, transposeonly=True)
    print out
    tmp = dofft(in1, pfft.Type.PFFT_C2R, pfft.Flags.PFFT_TRANSPOSED_IN)
    out = dofft(tmp, pfft.Type.PFFT_R2C, 0)

    print out / (4*4)

def dofft(i, type, flag, transposeonly=False):

    if transposeonly:
        axes = []
    else:
        axes = None
    if type == pfft.Type.PFFT_C2R:
        dir = pfft.Direction.PFFT_BACKWARD
    else:
        dir = pfft.Direction.PFFT_FORWARD

    procmesh = pfft.ProcMesh(np=[MPI.COMM_WORLD.size,])
    partition = pfft.Partition(type, [4, 4], procmesh, flag)

    buf1 = pfft.LocalBuffer(partition)
    out1 = pfft.LocalBuffer(partition)

    plan = pfft.Plan(partition, dir, buf1, out1, axes=axes)
    buf1.view_input()[:] = i

    plan.execute(buf1, out1)
    if transposeonly:
        return out1.view_input()
    return out1.view_output()
main()
