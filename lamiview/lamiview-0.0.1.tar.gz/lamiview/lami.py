# The MIT License (MIT)
#
# Copyright (c) 2016 Philippe Proulx <pproulx@efficios.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
import logging
import subprocess
from lamiview import utils
from functools import total_ordering


_logger = logging.getLogger(__name__)


class UnsupportedVersion(Exception):
    pass


class ExecError(Exception):
    def __init__(self, exit_status=None, output=None):
        self._exit_status = exit_status
        self._output = output

    @property
    def exit_status(self):
        return self._exit_status

    @property
    def output(self):
        return self._output

    def __str__(self):
        string = 'Execution error'

        if self._exit_status is not None:
            string += ': command returned exit status {}'.format(self._exit_status)

        return string


class ParseError(Exception):
    pass


class Error:
    def __init__(self, code, message):
        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    @classmethod
    def from_obj(cls, obj):
        msg = None
        code = None

        if 'error-code' in obj:
            code = obj['error-code']

        if 'error-message' in obj:
            msg = obj['error-message']

        return cls(code, msg)

    @property
    def dict(self):
        return self._dict


class _Data:
    UNIT = None
    NAME = None
    COLUMNS = None


class _SimpleValue(_Data):
    def __init__(self, value):
        super().__init__()
        self._value = value

    @property
    def value(self):
        return self._value

    @classmethod
    def from_obj(cls, obj):
        return cls(obj['value'])

    def __str__(self):
        if type(self) is float:
            return str(round(self._value, 3))

        return str(self._value)


class _SimpleName(_Data):
    def __init__(self, name):
        super().__init__()
        self._name = name

    @property
    def name(self):
        return self._name

    @classmethod
    def from_obj(cls, obj):
        return cls(obj['name'])

    def __str__(self):
        return str(self._name)


class Empty(_Data):
    CLASS = 'empty'
    NAME = 'Empty'

    def __str__(self):
        return ''


class Unknown(_Data):
    CLASS = 'unknown'
    NAME = 'Unknown'

    def __init__(self):
        super().__init__()

    @classmethod
    def from_obj(cls, obj):
        return cls()

    def __str__(self):
        return '?'


class Integer(_SimpleValue):
    CLASS = 'int'
    NAME = 'Integer'


class Number(_SimpleValue):
    CLASS = 'number'
    NAME = 'Number'


class String(_SimpleValue):
    CLASS = 'string'
    NAME = 'String'


class Bool(_SimpleValue):
    CLASS = 'bool'
    NAME = 'Boolean'

    def __str__(self):
        return 'Yes' if self._value else 'No'


class Ratio(_SimpleValue):
    CLASS = 'ratio'
    NAME = 'Ratio'

    def __str__(self):
        return '{} %'.format(self._value * 100)


class Timestamp(_SimpleValue):
    CLASS = 'timestamp'
    NAME = 'Timestamp'

    def __str__(self):
        return utils.format_timestamp(self._value)


class TimeRange(_Data):
    CLASS = 'time-range'
    NAME = 'Time range'
    COLUMNS = (
        ('beginning', 'begin'),
        ('ending', 'end'),
    )

    def __init__(self, begin, end):
        super().__init__()
        self._begin = begin
        self._end = end

    @property
    def begin(self):
        return self._begin

    @property
    def end(self):
        return self._end

    @classmethod
    def from_obj(cls, obj):
        return cls(obj['begin'], obj['end'])

    def __str__(self):
        begin = utils.format_timestamp(self._begin)
        end = utils.format_timestamp(self._end)

        return '{} -> {}'.format(begin, end)


class Duration(_SimpleValue):
    CLASS = 'duration'
    NAME = 'Duration'
    UNIT = 'µs'

    def __str__(self):
        return '{:.3f}'.format(round(self._value / 1000, 3))


class Size(_SimpleValue):
    CLASS = 'size'
    NAME = 'Size'

    def __str__(self):
        return utils.format_size(self._value)


class Bitrate(_SimpleValue):
    CLASS = 'bitrate'
    NAME = 'Bitrate'
    UNIT = 'bps'


class Syscall(_SimpleName):
    CLASS = 'syscall'
    NAME = 'System call'

    def __str__(self):
        return '{}()'.format(self._name)


class Process(_Data):
    CLASS = 'process'
    NAME = 'Process'
    COLUMNS = (
        ('name', 'name'),
        ('PID', 'pid'),
        ('TID', 'tid'),
    )

    def __init__(self, name, pid, tid):
        super().__init__()
        self._name = name
        self._pid = pid
        self._tid = tid

    @property
    def name(self):
        return self._name

    @property
    def pid(self):
        return self._pid

    @property
    def tid(self):
        return self._tid

    @classmethod
    def from_obj(cls, obj):
        name = Unknown()
        pid = Unknown()
        tid = Unknown()

        if 'name' in obj:
            name = String(obj['name'])

        if 'pid' in obj:
            pid = Integer(obj['pid'])

        if 'tid' in obj:
            tid = Integer(obj['tid'])

        return cls(name, pid, tid)

    def __str__(self):
        parts = []

        if type(self._name) is not Unknown:
            parts.append(str(self._name))

        if type(self._pid) is not Unknown:
            parts.append('(PID: {})'.format(self._pid))

        if type(self._tid) is not Unknown:
            parts.append('(TID: {})'.format(self._tid))

        if not parts:
            return '?'

        return ' '.join(parts)


class Path(_Data):
    CLASS = 'path'
    NAME = 'File system path'

    def __init__(self, path):
        super().__init__()
        self._path = path

    @property
    def path(self):
        return self._path

    @classmethod
    def from_obj(cls, obj):
        return cls(obj['path'])

    def __str__(self):
        return self._path


class FileDescriptor(_Data):
    CLASS = 'fd'
    NAME = 'File descriptor'

    def __init__(self, fd):
        super().__init__()
        self._fd = fd

    @property
    def fd(self):
        return self._fd

    @classmethod
    def from_obj(cls, obj):
        return cls(obj['fd'])

    def __str__(self):
        return str(self._fd)


class Irq(_Data):
    CLASS = 'irq'
    NAME = 'Interrupt'
    COLUMNS = (
        ('hard?', 'hard'),
        ('name', 'name'),
        ('number', 'nr'),
    )

    def __init__(self, hard, nr, name):
        super().__init__()
        self._hard = hard
        self._nr = nr
        self._name = name

    @property
    def hard(self):
        return self._hard

    @property
    def nr(self):
        return self._nr

    @property
    def name(self):
        return self._name

    def __str__(self):
        parts = []

        if self._hard:
            parts.append('Hard:')
        else:
            parts.append('Soft:')

        if type(self._name) is not Unknown:
            parts.append(str(self._name))

        if type(self._nr) is not Unknown:
            parts.append('(#{})'.format(self._nr))

        return ' '.join(parts)

    @classmethod
    def from_obj(cls, obj):
        hard = True
        nr = Unknown()
        name = Unknown()

        if 'hard' in obj:
            hard = Bool(obj['hard'])

        if 'nr' in obj:
            nr = Integer(obj['nr'])

        if 'name' in obj:
            name = String(obj['name'])

        return cls(hard, nr, name)


class Cpu(_Data):
    CLASS = 'cpu'
    NAME = 'CPU'

    def __init__(self, cpu_id):
        super().__init__()
        self._cpu_id = cpu_id

    @property
    def id(self):
        return self._cpu_id

    @classmethod
    def from_obj(cls, obj):
        return cls(obj['id'])

    def __str__(self):
        return str(self._cpu_id)


class Disk(_SimpleName):
    CLASS = 'disk'
    NAME = 'Disk'


class Part(_SimpleName):
    CLASS = 'part'
    NAME = 'Disk partition'


class NetIf(_SimpleName):
    CLASS = 'netif'
    NAME = 'Network interface'


class ColumnDescription:
    def __init__(self, title, cls, unit):
        super().__init__()
        self._title = title
        self._cls = cls
        self._unit = unit

    @property
    def title(self):
        return self._title

    @property
    def cls(self):
        return self._cls

    @property
    def unit(self):
        return self._unit

    @classmethod
    def from_obj(cls, obj):
        title = None
        column_cls = None
        unit = None

        if 'title' in obj:
            title = obj['title']

        if 'class' in obj:
            class_name = obj['class']

            if class_name in _data_class_names_to_class:
                column_cls = _data_class_names_to_class[class_name]
            else:
                print(class_name)
                column_cls = class_name

        if 'unit' in obj:
            unit = obj['unit']

        return cls(title, column_cls, unit)


class TableClass:
    def __init__(self, title, column_descriptions):
        self._title = title
        self._column_descriptions = column_descriptions

    @classmethod
    def from_obj(cls, obj):
        title = None
        column_descriptions = []

        if 'title' in obj:
            title = obj['title']

        if 'column-descriptions' in obj:
            for cd_obj in obj['column-descriptions']:
                column_descriptions.append(ColumnDescription.from_obj(cd_obj))

        return cls(title, column_descriptions)

    @property
    def title(self):
        return self._title

    @property
    def column_descriptions(self):
        return self._column_descriptions


@total_ordering
class Version:
    def __init__(self, major=0, minor=0, patch=0, extra=0):
        self._major = major
        self._minor = minor
        self._patch = patch
        self._extra = extra

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def patch(self):
        return self._patch

    @property
    def extra(self):
        return self._extra

    def _to_int(self):
        return self._major * 10000 + self._minor * 100 + self._patch

    def __eq__(self, other):
        if type(other) is not type(self):
            return False

        return self._to_int() == other._to_int()

    def __lt__(self, other):
        if type(other) is not type(self):
            return False

        return self._to_int() < other._to_int()

    def __str__(self):
        base = '{}.{}.{}'.format(self._major, self._minor, self._patch)

        if self._extra is not None:
            base += '-{}'.format(self._extra)

        return base

    @classmethod
    def from_obj(cls, obj):
        major = 0
        minor = 0
        patch = 0
        extra = None

        if 'major' in obj:
            major = obj['major']

        if 'minor' in obj:
            minor = obj['minor']

        if 'patch' in obj:
            patch = obj['patch']

        if 'extra' in obj:
            extra = obj['extra']

        return cls(major, minor, patch, extra)


class Metadata:
    def __init__(self, mi_version, version, title, authors, description,
                 url, tags, table_classes=None):
        self._mi_version = mi_version
        self._version = version
        self._title = title
        self._authors = authors
        self._description = description
        self._url = url
        self._tags = tags

        if table_classes is None:
            table_classes = {}

        self._table_classes = table_classes

    @property
    def mi_version(self):
        return self._mi_version

    @property
    def version(self):
        return self._version

    @property
    def title(self):
        return self._title

    @property
    def authors(self):
        return self._authors

    @property
    def description(self):
        return self._description

    @property
    def url(self):
        return self._url

    @property
    def tags(self):
        return self._tags

    @property
    def table_classes(self):
        return self._table_classes

    @classmethod
    def from_obj(cls, obj):
        mi_version = None
        version = None
        title = None
        authors = []
        description = None
        url = None
        tags = []

        if 'mi-version' in obj:
            mi_version = Version.from_obj(obj['mi-version'])

        if 'version' in obj:
            version = Version.from_obj(obj['version'])

        if 'title' in obj:
            title = obj['title']

        if 'authors' in obj:
            authors = obj['authors']

        if 'description' in obj:
            description = obj['description']

        if 'url' in obj:
            url = obj['url']

        if 'tags' in obj:
            tags = obj['tags']

        return cls(mi_version, version, title, authors, description, url, tags)

    @property
    def dict(self):
        return self._dict


class ResultTable:
    def __init__(self, time_range, cls, rows):
        super().__init__()
        self._time_range = time_range
        self._cls = cls
        self._rows = rows

    @property
    def time_range(self):
        return self._time_range

    @property
    def cls(self):
        return self._cls

    @property
    def rows(self):
        return self._rows

    @classmethod
    def from_obj(cls, obj):
        time_range = None
        rows = []

        if 'time-range' in obj:
            time_range = TimeRange.from_obj(obj['time-range'])

        if 'data' in obj:
            for row in obj['data']:
                cells = []

                for cell_obj in row:
                    cells.append(_data_from_obj(cell_obj))

                rows.append(cells)

        return cls(time_range, None, rows)


class AnalysisResults:
    def __init__(self, result_tables, metadata):
        super().__init__()
        self._result_tables = result_tables
        self._metadata = metadata

    @property
    def result_tables(self):
        return self._result_tables

    @property
    def metadata(self):
        return self._metadata

    @property
    def dict(self):
        return self._dict


class ProgressUpdate:
    def __init__(self, value, msg):
        self._value = value
        self._msg = msg

    @property
    def value(self):
        return self._value

    @property
    def message(self):
        return self._msg

    @classmethod
    def from_line(cls, line):
        first_space_pos = line.find(' ')
        msg = None
        number = line

        if first_space_pos >= 0:
            number = line[:first_space_pos]
            msg = line[first_space_pos + 1:]

        try:
            number = float(number)
        except:
            return

        return cls(number, msg)


_data_classes = (
    Integer,
    Number,
    String,
    Bool,
    Unknown,
    Ratio,
    Timestamp,
    TimeRange,
    Duration,
    Size,
    Bitrate,
    Syscall,
    Process,
    Path,
    FileDescriptor,
    Irq,
    Cpu,
    Disk,
    Part,
    NetIf,
)


_data_class_names_to_class = {cls.CLASS: cls for cls in _data_classes}


def _data_from_obj(obj):
    if type(obj) is dict and 'class' in obj:
        cls = _data_class_names_to_class[obj['class']]
    else:
        if type(obj) is int:
            return Integer(obj)
        elif type(obj) is float:
            return Number(obj)
        elif type(obj) is str:
            return String(obj)
        elif type(obj) is bool:
            return Bool(obj)
        elif type(obj) is None:
            return Empty()
        else:
            return Unknown()

    return cls.from_obj(obj)


def _table_class_from_obj(obj, table_classes):
    table_class = TableClass.from_obj(obj)

    if 'inherit' in obj:
        parent = table_classes[obj['inherit']]

        if table_class.title is None:
            table_class._title = parent.title

        if not table_class.column_descriptions:
            table_class._column_descriptions = parent.column_descriptions

    return table_class


def _metadata_from_obj(obj):
    metadata = Metadata.from_obj(obj)
    table_classes = {}

    if 'table-classes' not in obj:
        return metadata

    for table_class_name, table_class_obj in obj['table-classes'].items():
        table_classes[table_class_name] = _table_class_from_obj(table_class_obj,
                                                                table_classes)

    metadata._table_classes = table_classes

    return metadata


def _result_table_from_obj(obj, table_classes):
    result_table = ResultTable.from_obj(obj)

    if type(obj['class']) is str:
        table_class = table_classes[obj['class']]
    else:
        table_class = _table_class_from_obj(obj['class'], table_classes)

    result_table._cls = table_class

    return result_table


def _analysis_results_from_obj(obj, metadata):
    result_tables = []

    for result_obj in obj['results']:
        result_table = _result_table_from_obj(result_obj,
                                              metadata.table_classes)
        result_tables.append(result_table)

    return AnalysisResults(result_tables, metadata)


def _error_or_other_from_obj(obj, other_fn):
    if 'error-code' in obj or 'error-message' in obj:
        model_obj = Error.from_obj(obj)
    else:
        model_obj = other_fn(obj)

    model_obj._dict = obj

    return model_obj


def get_metadata(cmd):
    full_cmd = '{} --metadata'.format(cmd)
    _logger.info('Getting metadata with full command: {}'.format(full_cmd))

    try:
        output = subprocess.check_output(full_cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        _logger.error('Cannot get metadata: command returned {}'.format(e.returncode))
        raise ExecError(e.returncode, e.output) from e
    except Exception as e:
        _logger.error('Cannot get metadata')
        raise ExecError() from e

    _logger.info('Parsing metadata')

    try:
        output = output.decode()
        json_data = json.loads(output)
    except Exception as e:
        _logger.error('Cannot parse metadata')
        raise ParseError('Cannot parse metadata') from e

    if 'mi-version' in json_data:
        mi_version = Version.from_obj(json_data['mi-version'])

        if mi_version > Version(0, 1):
            raise UnsupportedVersion('Unsupported MI version: {}'.format(mi_version))

    try:
        ret = _error_or_other_from_obj(json_data, _metadata_from_obj)
    except Exception as e:
        _logger.error('Cannot parse metadata')
        raise ParseError('Cannot parse metadata') from e

    return ret


def get_analysis_results(cmd, path, begin, end, limit, output_progress,
                         on_progress_update=None):
    def analysis_results_from_obj(obj):
        return _analysis_results_from_obj(obj, metadata)

    full_cmd = cmd

    if begin is not None:
        full_cmd += ' --begin={}'.format(begin)

    if end is not None:
        full_cmd += ' --end={}'.format(end)

    if limit is not None:
        full_cmd += ' --limit={}'.format(limit)

    if output_progress:
        full_cmd += ' --output-progress'

    full_cmd += " '{}'".format(path)
    metadata = get_metadata(cmd)

    if type(metadata) is Error:
        return metadata

    json_lines = []
    in_progress = True
    _logger.info('Getting analysis results with full command: {}'.format(full_cmd))

    try:
        p = subprocess.Popen(full_cmd, shell=True, stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE, bufsize=1,
                             universal_newlines=True)

        with p.stdout:
            for line in p.stdout:
                if line.endswith('\n'):
                    line = line[:-1]

                if in_progress:
                    if len(line.strip()) == 0:
                        continue

                    progress_update = ProgressUpdate.from_line(line)

                    if progress_update is None:
                        in_progress = False
                    else:
                        if on_progress_update is not None:
                            on_progress_update(progress_update)

                if not in_progress:
                    json_lines.append(line)

        _logger.info('Waiting for the command to complete')
        p.wait()
    except Exception as e:
        import traceback
        traceback.print_exc()
        _logger.error('Cannot get analysis results')
        raise ExecError() from e

    _logger.info('Parsing analysis results')

    try:
        output = '\n'.join(json_lines)
        json_data = json.loads(output)
        ret = _error_or_other_from_obj(json_data, analysis_results_from_obj)
    except Exception as e:
        _logger.error('Cannot parse analysis results')
        raise ParseError('Cannot parse analysis results') from e

    return ret
