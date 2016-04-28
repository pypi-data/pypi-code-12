#!/usr/bin/env python

from PIL import Image

im = Image.new('RGB', (2048, 2048))
for _ in range(10):
    im.resize((200, 2048), Image.LANCZOS)

