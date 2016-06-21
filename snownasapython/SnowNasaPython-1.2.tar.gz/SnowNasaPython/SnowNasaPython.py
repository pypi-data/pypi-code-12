import sys
from apod import Apod

class SnowNasaPython(object):

  def get_pic(api_key):
    pic = Apod.get_apod_pic(Apod(api_key))
    return pic


