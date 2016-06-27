#!/usr/bin/env python

import neuroglancer
import numpy as np
import signal
import sys

def stop(signal, frame):
    neuroglancer.stop()
    sys.exit(0)

a = np.ones((100,100,100), dtype=np.uint8)*255
b = np.random.randint(0, 100, (100,1000,1000), dtype=np.uint64)

layers = [
    ('a', a),
    ('b', b)
]

print neuroglancer.serve(layers, server_args = { 'bind_address': '127.0.0.1', 'bind_port': 8484 })

signal.signal(signal.SIGINT, stop)
print('Server started, press Ctrl+C to stop')
signal.pause()
