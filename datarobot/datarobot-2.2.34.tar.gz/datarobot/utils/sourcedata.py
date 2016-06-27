import os

import pandas as pd
import six

from .. import errors


def dataframe_to_buffer(df):
    """Convert a dataframe to a serialized form in a buffer

    Parameters
    ----------
    df : pandas.DataFrame
        The data to serialize

    Returns
    -------
    buff : StringIO()
        The data. The descriptor will be reset before being returned (seek(0))
    """
    buff = six.StringIO()
    df.to_csv(buff, encoding='utf-8', index=False)
    buff.seek(0)
    return buff


def is_urlsource(sourcedata):
    """ Whether sourcedata is of url kind
    """
    return isinstance(sourcedata, six.string_types) and sourcedata.startswith('http')


def recognize_sourcedata(sourcedata, default_fname):
    """Given a sourcedata figure out if it is a filepath, dataframe, or
    filehandle, and then return the correct kwargs for the upload process
    """
    if isinstance(sourcedata, pd.DataFrame):
        buff = dataframe_to_buffer(sourcedata)
        return {'filelike': buff,
                'fname': default_fname}
    elif hasattr(sourcedata, 'read') and hasattr(sourcedata, 'seek'):
        return {'filelike': sourcedata,
                'fname': default_fname}
    elif isinstance(sourcedata, six.string_types) and os.path.isfile(sourcedata):
        try:
            sourcedata.encode('ascii')
        # Which exception we get here depends on whether the input was string or unicode
        # (we allow both)
        except (UnicodeEncodeError, UnicodeDecodeError):
            raise errors.IllegalFileName
        return {'file_path': sourcedata,
                'fname': os.path.split(sourcedata)[1]}
    elif isinstance(sourcedata, six.binary_type) and not is_urlsource(sourcedata):
        assert_modelable(sourcedata)
        return {'content': sourcedata,
                'fname': default_fname}

    err_msg = ('sourcedata parameter not understood. Use pandas '
               'DataFrame, file object or string that is either a '
               'path to file or raw file content to specify data '
               'to upload')
    raise errors.InputNotUnderstoodError(err_msg)


def assert_modelable(sourcedata):
    """
    Uses a heuristic to assert that the given argument is not a
    filepath.

    Some users have mistyped filepaths before, which
    the function `recognize_sourcedata` interpreted as being
    the actual data to use for modeling. This would lead to other
    problems later on.

    Parameters
    ----------
    sourcedata : six.binary_type
        The data which we are trying to assert is not a mistyped
        file path.

    Raises
    ------
    InputNotUnderstoodError
        If this does look like a filepath (it should not)
    """
    if len(sourcedata) < 500 and len(sourcedata.splitlines()) == 1:
        raise errors.InputNotUnderstoodError(
            'The argument for sourcedata has only one line. This is not sensible data for '
            'modeling (did you mistype a file path?)')
