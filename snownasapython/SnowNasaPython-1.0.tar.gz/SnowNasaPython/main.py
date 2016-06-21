import sys
from apod import Apod

class SnowNasaPython(object):

  def get_pic(api_key):
    pic = Apod.get_apod_pic(Apod(api_key))
    return pic


  #if __name__=="__main__":
  #  api_key = raw_input("Please enter your Nasa API key here: ")
  #  get_pic(api_key)
  
