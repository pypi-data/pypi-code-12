import pandas as pd
import pytest
from fennec.testing import almost_equal
from fennec.utils.index import mae, mse, rmse, r2

def pytest_funcarg__data(request):
    iris = pd.read_csv("https://raw.githubusercontent.com/pydata/pandas/master/doc/data/iris.data")
    return iris.ix[:, 0], iris.ix[:, 1]

def test_mse(data):
    expected = 8.726267
    assert almost_equal(mse(data[0], data[1]), expected)

def test_mae(data):
    expected = 2.789333
    assert almost_equal(mae(data[0], data[1]), expected)

def test_rmse(data):
    expected = 2.954026
    assert almost_equal(rmse(data[0], data[1]), expected)

def test_r2(data):
    expected = -11.8116
    assert almost_equal(r2(data[0], data[1]), expected)
