import urllib.request

import pytest
from more_itertools.recipes import flatten

from jaraco.stream import gzip


@pytest.fixture
def gzip_stream():
	url = 'https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz'
	return urllib.request.urlopen(url)


def test_lines_from_stream(gzip_stream):
	chunks = gzip.read_chunks(gzip_stream)
	streams = gzip.load_streams(chunks)
	lines = flatten(map(gzip.lines_from_stream, streams))
	first_line = next(lines)
	assert first_line == '['
