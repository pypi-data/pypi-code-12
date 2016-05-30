#!/usr/bin/env python

import sys
import re
import StringIO
import collections

re_parsedecl = re.compile(r"^(\w+) (\w+)\((.*)\);$")
re_parseparam = re.compile(r"^(.*?)(\w+)$")

def splitparam(p):
    m = re_parseparam.match(p)
    if m:
        return (m.group(1).strip(), m.group(2))
    else:
        print >>sys.stderr, "Failed to parse parameter", p
        return None

def compare_param(x, y):
    if x[0] and y[0] and (x[0] != y[0]):
        return False
    elif x[1] and y[1] and (x[1] != y[1]):
        return False
    else:
        return True

merge_params = (
    (
        ("","numEventsInWaitList"),
        ("","eventWaitList"),
        "eventWaitList"
    ),
    (
        ("", "numCommandQueues"),
        ("", "commandQueues"),
        "commandQueues"
    ),
)

remove_params = (
    ("cl_event *", "events"),
    ("cl_int *", "err"),
    ("size_t *", "fullsize"),
    ("size_t *", "ld"),
)

params_description = (
    (r"clblas[SDCZ](gemm)", ("clblasOrder", "order"),  "Row/column order"),
    (r"clblas[SDCZ](gemm)", ("clblasTranspose", "transA"),  "How matrix A is to be transposed"),
    (r"clblas[SDCZ](gemm)", ("clblasTranspose", "transB"),  "How matrix B is to be transposed"),
    (r"clblas[SDCZ](gemm)", ("size_t", "M"),  "Number of rows in matrix A"),
    (r"clblas[SDCZ](gemm)", ("size_t", "K"),  "Number of columns in matrix A and rows in matrix B"),
    (r"clblas[SDCZ](gemm)", ("size_t", "N"),  "Number of columns in matrix B"),
    (r"clblas[SDCZ](gemm)", ("size_t", "offB"),  "Offset of the first element of the matrix B in the buffer object. Counted in elements."),
    (r"clblas[SDCZ](gemm)", ("size_t", "ldb"),  "Leading dimension of matrix B."),
    (r"clblas[SDCZ](gemm)", ("size_t", "offC"),  "Offset of the first element of the matrix C in the buffer object. Counted in elements."),
    (r"clblas[SDCZ](gemm)", ("size_t", "ldc"),  "Leading dimension of matrix C."),
    (r"clblas[SDCZ](gemm)", ("", "alpha"),  "The constant factor for matrix A."),
    (r"clblas[SDCZ](gemm)", ("", "beta"),  "The constant factor for matrix C."),
    (r"clblas[SDCZ](gemm)", ("cl_mem", "B"),  "Buffer object storing matrix B"),
    (r"clblas[SDCZ](gemm)", ("cl_mem", "C"),  "Buffer object storing matrix C"),
    (r"clblas[SDCZ](gemm)", ("const cl_mem", "B"),  "Buffer object storing matrix B"),
    (r"clblas[SDCZ](gemm)", ("const cl_mem", "C"),  "Buffer object storing matrix C"),
    (r"clblas[SDCZ](gemm|gemv|gbmv|ger)", ("size_t", "offA"),  "Offset of the first element of the matrix A in the buffer object. Counted in elements."),
    (r"clblas[SDCZ](gemm|gemv|gbmv|ger)", ("size_t", "offa"),  "Offset of the first element of the matrix A in the buffer object. Counted in elements."),
    (r"clblas[SDCZ](gemm|gemv|gbmv|ger)", ("size_t", "lda"),  "Leading dimension of matrix A."),
    (r"clblas[SDCZ](gemm|gemv|gbmv|ger)", ("cl_mem", "A"),  "Buffer object storing matrix A"),
    (r"clblas[SDCZ](gemm|gemv|gbmv|ger)", ("const cl_mem", "A"),  "Buffer object storing matrix A"),
    (r"clblas[SDCZ](gemv|gbmv|ger)", ("size_t", "M"),  "Number of rows in matrix A"),
    (r"clblas[SDCZ](gemv|gbmv|ger)", ("size_t", "N"),  "Number of columns in matrix A"),
    (r"clblas[SDCZ](gemv|gbmv)", ("", "beta"),  "The constant factor for vector Y"),
    (r"clblas[SDCZ](dot[uc]?)", ("cl_mem", "dotProduct"),  "Buffer object that will contain the dot-product value."),
    (r"clblas[SDCZ](dot[uc]?)", ("size_t", "offDP"),  "Offset to dot-product in dotProduct buffer object. Counted in elements."),
    (r"clblas[SDCZ](dot[uc]?)", ("cl_mem", "scratchBuff"),  "Temporary cl_mem scratch buffer object of minimum size N elements."),
    (r"clblas[SDCZ](nrm2)", ("cl_mem", "scratchBuff"),  "Temporary cl_mem scratch buffer object of minimum size 2*N elements."),
    (r"clblas[SDCZ](gbmv)", ("size_t", "KL"),  "Number of sub-diagonals in banded matrix A."),
    (r"clblas[SDCZ](gbmv)", ("size_t", "KU"),  "Number of super-diagonals in banded matrix A."),
    (r"clblas[SDCZ](gbmv)", ("clblasTranspose", "trans"), "How matrix A is to be transposed."),
    (r"clblas[SDCZ](nrm2)", ("cl_mem", "NRM2"), "Buffer object that will contain the NRM2 value."),
    (r"clblas[SDCZ](nrm2)", ("size_t", "offNRM2"), "Offset to NRM2 value in NRM2 buffer object. Counted in elements."),
    (r"clblas[SDCZ]([sd]?rot)", ("", "C"), "specifies the cosine, cos. This number is real."),
    (r"clblas[SDCZ]([sd]?rot)", ("", "S"), "specifies the sine, sin. This number is real."),

    (r"clblas[S](s?rotg)", ("cl_mem", "SA"), "Buffer object that contains float32 scalar SA"),
    (r"clblas[D](s?rotg)", ("cl_mem", "DA"), "Buffer object that contains float64 scalar DA"),
    (r"clblas[C](s?rotg)", ("cl_mem", "CA"), "Buffer object that contains complex64 scalar CA"),
    (r"clblas[Z](s?rotg)", ("cl_mem", "CA"), "Buffer object that contains complex128 scalar CA"),
    (r"clblas[S](s?rotg)", ("cl_mem", "SB"), "Buffer object that contains float32 scalar SB"),
    (r"clblas[D](s?rotg)", ("cl_mem", "DB"), "Buffer object that contains float64 scalar DB"),
    (r"clblas[C](s?rotg)", ("cl_mem", "CB"), "Buffer object that contains complex64 scalar CB"),
    (r"clblas[Z](s?rotg)", ("cl_mem", "CB"), "Buffer object that contains complex128 scalar CB"),
    (r"clblas[S](s?rotg)", ("size_t", "offSA"), "Offset to SA in SA buffer object. Counted in elements."),
    (r"clblas[D](s?rotg)", ("size_t", "offDA"), "Offset to DA in DA buffer object. Counted in elements."),
    (r"clblas[CZ](s?rotg)", ("size_t", "offCA"), "Offset to CA in CA buffer object. Counted in elements."),
    (r"clblas[D](s?rotg)", ("size_t", "offDB"), "Offset to DB in DB buffer object. Counted in elements."),
    (r"clblas[CZ](s?rotg)", ("size_t", "offCB"), "Offset to CB in CB buffer object. Counted in elements."),
    (r"clblas[SDCZ](s?rotg)", ("cl_mem", "C"), "Buffer object that contains scalar C.  C is real."),
    (r"clblas[SDCZ](s?rotg)", ("cl_mem", "S"), "Buffer object that contains scalar S."),
    (r"clblas[SDCZ](s?rotg)", ("size_t", "offC"), "Offset to C in C buffer object. Counted in elements."),
    (r"clblas[SDCZ](s?rotg)", ("size_t", "offS"), "Offset to S in S buffer object. Counted in elements."),

    (r"clblas[S](s?rotm)", ("size_t", "offSparam"), "Offset of first element of array SPARAM in buffer object. Counted in elements."),
    (r"clblas[D](s?rotm)", ("size_t", "offDparam"), "Offset of first element of array DPARAM in buffer object. Counted in elements."),
    (r"clblas[S](s?rotm)", ("cl_mem", "SPARAM"), "Buffer object that contains at least 5 float32 scalars.  SPARAM(1)=SFLAG SPARAM(2)=SH11 SPARAM(3)=SH21 SPARAM(4)=SH12 SPARAM(5)=SH22"),
    (r"clblas[D](s?rotm)", ("cl_mem", "DPARAM"), "Buffer object that contains at least 5 float64 scalars.  DPARAM(1)=DFLAG DPARAM(2)=DH11 DPARAM(3)=DH21 DPARAM(4)=DH12 DPARAM(5)=DH22"),

    (r"clblas.*", ("", "commandQueues"), "List or tuple containing pyopencl.CommandQueue instances"),
    (r"clblas.*", ("", "eventWaitList"), "List or tuple containing pyopencl.Event instances"),
    (r"clblas.*", ("clblasOrder", "order"), "Row/Column order."),
    (r"clblas.*", ("clblasTranspose", "transA"), "How matrix A is to be transposed."),
    (r"clblas.*", ("clblasTranspose", "transB"), "How matrix B is to be transposed."),
    (r"clblas.*", ("int", "incx"), "Increment for the elements of X. Must not be zero."),
    (r"clblas.*", ("int", "incy"), "Increment for the elements of Y. Must not be zero."),
    (r"clblas.*", ("size_t", "offx"), "Offset of first element of vector X in buffer object. Counted in elements."),
    (r"clblas.*", ("size_t", "offy"), "Offset of first element of vector Y in buffer object. Counted in elements."),
    (r"clblas.*", ("const cl_mem", "X"),  "Buffer object storing vector X"),
    (r"clblas.*", ("const cl_mem", "Y"),  "Buffer object storing vector Y"),
    (r"clblas.*", ("cl_mem", "X"),  "Buffer object storing vector X"),
    (r"clblas.*", ("cl_mem", "Y"),  "Buffer object storing vector Y"),
    (r"clblas.*", ("const cl_mem", "x"),  "Buffer object storing vector x"),
    (r"clblas.*", ("const cl_mem", "y"),  "Buffer object storing vector y"),
    (r"clblas.*", ("cl_mem", "x"),  "Buffer object storing vector x"),
    (r"clblas.*", ("cl_mem", "y"),  "Buffer object storing vector y"),
    (r"clblas[SDCZ](axpy|swap|scal|[sd]scal|copy|dot|dot[uc]|nrm2|[ds]?rot|rotm)", ("size_t", "N"),  "Number of elements in vector X"),
    (r"clblas[SDCZ](axpy|scal|[sd]scal|gemv|gbmv|ger)", ("", "alpha"),  "The constant factor for vector X"),
)

def gen_output(fpath):
    stdout = sys.stdout
    sys.stdout = StringIO.StringIO()
    print "import pyclblas_swig"
    print ""
    print """
from pyclblas_swig import clblasRowMajor
from pyclblas_swig import clblasColumnMajor
from pyclblas_swig import clblasNoTrans
from pyclblas_swig import clblasTrans
from pyclblas_swig import clblasConjTrans
from pyclblas_swig import clblasUpper
from pyclblas_swig import clblasLower
from pyclblas_swig import clblasUnit
from pyclblas_swig import clblasNonUnit
from pyclblas_swig import clblasLeft
from pyclblas_swig import clblasRight
"""
    num_undocumented = 0
    num_documented = 0
    
    undocumented_args = collections.defaultdict(lambda: 0)

    with open(fpath, 'r') as fin:
        for line in fin:
            match = re_parsedecl.match(line)
            rettype = match.group(1)
            name = match.group(2)
            params = [splitparam(x.strip()) for x in match.group(3).split(",") if x]

            for cp in remove_params:
                compares = list(compare_param(cp, p) for p in params)
                if any(compares):
                    params.pop(compares.index(True))

            for rule in merge_params:
                check_params = rule[:-1]
                result = rule[-1]

                bad = False
                idx = []
                for cp in check_params:
                    compares = list(compare_param(cp, p) for p in params)
                    if not any(compares):
                        bad = True
                        break
                    else:
                        idx.append(compares.index(True))

                if not bad:
                    idx.sort(reverse=True)
                    for i in idx:
                        params.pop(i)
                    
                    params.insert(idx[-1], ("", result))

            docstring = ""
            all_documented = True
            any_documented = False
            for p in params:
                documented = False
                for re_func, cp, desc in params_description:
                    if re.match(re_func + "$", name) and compare_param(cp, p):
                        if p[0]:
                            docstring += "    :param %s: [%s] %s\n" % (cp[1], p[0].replace("*","\\*"), desc)
                        else:
                            docstring += "    :param %s: %s\n" % (cp[1], desc)
                        documented = True
                        break

                if not documented:
                    if p[0]:
                        docstring += "    :param %s: [%s] %s\n" % (p[1], p[0].replace("*","\\*"), "TODO")
                    else:
                        docstring += "    :param %s: %s\n" % (p[1], "TODO")
                    
                    undocumented_args[(p[0],p[1])] += 1
                all_documented = documented and all_documented
                any_documented = documented or any_documented

            #if any_documented:
            docstring += "\n"

            if not all_documented:
                docstring += "    TODO: Not all parameters are documented!\n"
                num_undocumented += 1
            else:
                num_documented += 1

            if docstring:
                docstring = '    """' + docstring + '    """\n'
                

            s_params = ", ".join(x[1] for x in params)
            print "def %s(%s):\n%s    return pyclblas_swig.%s(%s)\n" % (name, s_params, docstring, name, s_params)
    ret = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = stdout

    print >>sys.stderr, "Total Undocumented:", num_undocumented, "Total Documented:", num_documented
    print >>sys.stderr, sorted(undocumented_args.items(), key=lambda x: x[1], reverse=True)[:10]

    return ret



