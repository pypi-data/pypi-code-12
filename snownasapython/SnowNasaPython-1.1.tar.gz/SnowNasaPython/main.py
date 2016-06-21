import sys
from apod import Apod
from SnowNasaPython import SnowNasaPython

if __name__=="__main__":
  api_key = raw_input("Please enter your Nasa API key here: ")
  get_pic(api_key)
  
