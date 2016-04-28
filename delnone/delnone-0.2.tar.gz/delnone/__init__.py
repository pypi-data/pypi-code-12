import pytest
import collections
import json
import sys

def delnone(i):
  if isinstance(i, dict):
    o = {}
    for (key, value) in i.items():
      value = delnone(value)
      if value is not None:
        o[key] = value
  elif isinstance(i, list):
    o = []
    for value in i:
      value = delnone(value)
      if value is not None:
        o.append(value)
  else:
    o = i
  return o

