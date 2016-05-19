import pytest

from stringtopy import str_to_float_converter

@pytest.fixture
def default_str_to_float():
    return str_to_float_converter()
