import numpy
from numpy.testing import assert_equal, assert_array_equal, run_module_suite
from kdcount.utils import constant_array

def test_c_array_scalar():
    shape = (3, 1, 2, 3)
    c = constant_array(shape=shape)
    c.value[...] = 1
    assert_equal(c, 1)
    assert_equal(c.shape, shape)

def test_c_array_record():
    shape = (3, 1, 2, 3)
    c = constant_array(shape=shape, dtype=[('f1', 'f4')])
    c.value['f1'] = 1
    assert_equal(c['f1'], 1)
    assert_equal(c.shape, shape)

def test_c_array_shape():
    shape = (3, 1, 2, 3)
    c = constant_array(shape=shape, dtype=('f4', 3))
    c.value[...] = 1
    assert_equal(c, 1)
    assert_equal(c.shape, list(shape) + [3])

def test_c_array_index():
    shape = (3, 1, 2, 3)
    c = constant_array(shape=shape)
    c.value[...] = 1
    assert_equal(c[0].shape, shape[1:])
    assert_equal(c[[0, 1]].shape, [2] + list(shape[1:]))
    ind = numpy.array([0, 1], dtype='intp')
    assert_equal(c[ind].shape, [2] + list(shape[1:]))
    v = c[[0, 1]]
    assert_array_equal(v.strides, 0)
    
