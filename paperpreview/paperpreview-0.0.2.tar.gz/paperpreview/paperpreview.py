import sys
import os

from wand.image import Image, FILTER_TYPES
from wand.color import Color


def preview(pdfpath, outpath, croph):
  """
  @arg pdfpath input pdf path
  @arg outpath output screeshot file path
  @arg croph percentage of the page height to crop at
  """
  try:
    with Image(filename=pdfpath) as imgs:
      for imgidx, img in enumerate(imgs.sequence):
        w, h = img.width, img.height
        h = int(croph * h)
        img.crop(0, 0, width=w, height=h)

        newimg = Image(width=w, height=h, background=Color("white"))
        newimg.composite(img, 0, 0)
        newimg.convert("png")
        newimg.save(filename=outpath)
        return True
  except Exception as err:
    print err
    return False

