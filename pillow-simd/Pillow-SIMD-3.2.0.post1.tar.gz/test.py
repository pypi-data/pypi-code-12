#!/usr/bin/env python

from PIL import Image
import time

im = Image.new('RGB', (4096, 4096))

times = []
for _ in range(5):
    start = time.time()
    im.resize((512, 512), Image.LANCZOS)
    times.append(time.time() - start)
    print '.'

times.sort()
print '>>>', times[len(times) // 3]
