import numpy as np
import pandas as pd

from fennec.utils.array import as_vector


def pytest_generate_tests(metafunc):
    if "vector_like" in metafunc.funcargnames:
        metafunc.parametrize("vector_like", [
            np.array([0, 1, 2]),
            np.array([[0, 1, 2]]),
            np.array([[0], [1], [2]]),
            pd.Series([0, 1, 2]),
            pd.DataFrame([0, 1, 2]),
            pd.DataFrame([[0], [1], [2]])
        ])


def pytest_funcarg__answer_vector(request):
    return np.array([0, 1, 2])


def test_as_vector(vector_like, answer_vector):
    assert (as_vector(vector_like) == answer_vector).all()
