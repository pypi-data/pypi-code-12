from distutils.core import setup
import os
import sys
setup(
  name = 'WillPy',
  packages = ['WillPy'],
  version = '3.2',
  description = 'A smart personal assistant',
  author = 'Will Beddow',
  author_email = 'WillPy@willbeddow.com',
  url = 'https://github.com/ironman5366/WillPy',
  download_url = 'https://github.com/ironman5366/WillPy/tarball/3.2',
  keywords = ['Personal Assistant', 'Plugins'],
  classifiers = [],
)
os.chdir(os.path.dirname(os.path.realpath(__file__)))
if sys.platform == 'win32':
    if os.path.isdir("/Python27"):
        os.system("/Python27/Scripts/pip.exe install -r requirements.txt")
elif 'lin' in sys.platform or "darwin" in sys.platform:
    os.system("sudo pip install -r requirements.txt")
def wolfram_setup():
    wolframalpha_key = raw_input("Please enter a wolframalpha key. You can get one from http://products.wolframalpha.com/api/>")
    if wolframalpha_key:
        import WillPy.config as config
        config.add_config({"wolfram" : [wolframalpha_key]})
    else:
        if raw_input("This is a required step for setup, are you sure you want to quit? (y/n)").lower() != "y":
            wolfram_setup()
wolfram_setup()