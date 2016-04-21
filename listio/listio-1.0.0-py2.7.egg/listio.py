import unicodecsv as csv
import sys


COMMENT_CHAR = '#'

CSV_DELIMITER = ';'
CSV_LINETERMINATOR = '\n'


def strip_comments_and_empty_lines(lines):
    for line in lines:
        if not line.startswith(COMMENT_CHAR) and line.strip():
            yield line.strip()


def _read_csv(file_path):
    return csv.reader(
        read_lines(file_path),
        delimiter=CSV_DELIMITER
    )


def _write_csv(file_path, data):
    with open(file_path, 'a') as f:
        writer = csv.writer(
            f,
            delimiter=CSV_DELIMITER,
            lineterminator=CSV_LINETERMINATOR
        )
        writer.writerows(data)


def read_lines(file_path):
    with open(file_path, 'r') as f:
        for line in strip_comments_and_empty_lines(f):
            yield line


def read_map(file_path):
    return _read_csv(file_path)


def write_map(file_path, data):
    return _write_csv(file_path, data)


def read_list(file_path):
    return [item[0] for item in _read_csv(file_path)]


def write_list(file_path, data):
    _write_csv(
        file_path,
        [[item] for item in data]
    )
