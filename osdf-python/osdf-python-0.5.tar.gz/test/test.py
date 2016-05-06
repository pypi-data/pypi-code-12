#!/usr/bin/env python

from osdf import OSDF

client = OSDF("osdf-devel.igs.umaryland.edu", "test", "test", port=8123, ssl=True)

info = client.get_info()
print(info)
