import datetime

import handwritingio


def test_decode_timestamps():
  obj = {'time': '2006-01-02T15:04:05.000007000Z'}
  decoded = handwritingio._decode_timestamps(obj)
  assert isinstance(decoded['time'], datetime.datetime)
  assert decoded['time'].month == 1
  assert decoded['time'].day == 2
  assert decoded['time'].hour == 15
  assert decoded['time'].minute == 4
  assert decoded['time'].second == 5
  assert decoded['time'].year == 2006
  assert decoded['time'].microsecond == 7


def test_decode_timestamps_deep():
  obj = {'foo': {'time': '2006-01-02T15:04:05.000007000Z'}}
  decoded = handwritingio._decode_timestamps(obj)
  assert isinstance(decoded['foo']['time'], datetime.datetime)


def test_auto_decode(test_handwriting):
  assert isinstance(test_handwriting['date_created'], datetime.datetime)
