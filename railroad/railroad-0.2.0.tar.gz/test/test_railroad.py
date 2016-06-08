"""
Tests for `railroad` module.
"""
import pytest

from mock import Mock, call

from railroad import (
    prepare,
    catch,
    get_or_reraise,
    compose,
)


def test_get_or_reraise_return_data_if_has_no_error():
    data = ('test', None)

    result = get_or_reraise(data)

    assert result == 'test'


def test_get_or_reraise_reraise_given_errror():
    data = (None, Exception())
    with pytest.raises(Exception):
        get_or_reraise(data)


def test_call_compose_with_right_order():
    f = compose(lambda x: x + 'a', lambda x: x + 'b')
    assert f('') == 'ab'


def test_catch_given_error_and_call_function():
    ex = Exception()
    data = (None, ex)
    f = Mock()

    c = catch(Exception, f)

    result = c(data)

    assert f.called
    assert f.call_args == call(ex)

    assert result[0] == f.return_value
    assert result[1] is None


def test_catch_return_data_when_no_error():
    data = ('test', None)

    f = Mock()

    c = catch(Exception, f)

    result = c(data)

    assert not f.called

    assert result == data


def test_prepare_catch_exception_and_return_it_in_tuple():
    f = Mock(side_effect=Exception)
    fn = prepare(f)

    result = fn()

    assert result[0] is None
    assert isinstance(result[1], Exception)


def test_prepare_return_result_from_given_function_in_tuple():
    f = Mock()
    fn = prepare(f)

    result = fn()

    assert result[0] == f.return_value
    assert result[1] is None
