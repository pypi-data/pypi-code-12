

######################################################################################
#
# YOU CAN / SHOULD EDIT THE FOLLOWING SETTING
#
######################################################################################

PKG_NAME = 'dynamet'


VERSION = (2, 8, 6)

### install package as emzed extension ? #############################################
#   -> package will appear in emzed.ext namespace after installation

IS_EXTENSION = True


### install package as emzed app ?  ##################################################
#   -> can be started as app.dynamet()
#   set this variable to None if this is a pure extension and not an emzed app

APP_MAIN = "dynamet.app:run"


### author information ###############################################################

AUTHOR = 'Patrick Kiefer'
AUTHOR_EMAIL = 'kiefer@micro.biol.ethz.ch'
AUTHOR_URL = ''

# HINT: to modify version edit dynamet/version.py !!!


### package descriptions #############################################################

DESCRIPTION = "an automated pipeline for LC-MS based dynamic labeling data"
LONG_DESCRIPTION = """
DynaMet is a fully automated workflow for liquid chromatography mass spectrometry (LC-MS) raw
 data analyses allowing for metabolome-wide investigations of dynamic isotope labeling experiments. 
 DynaMet enables untargeted extraction of labeling profiles by grouping metabolite features 
 in different samples with isotopic patterns changing over time. 
 Integrated tools for expressive data visualization enhance result inspection. 
 REMARK: For straight forward installation of DynaMet type command `!pip install dynamet` in emzed
 IPython console and press enter. DynaMet app will be available after opening a new IPython 
 console.
 Changes in Version 2.8.0:
    - provides additional fitting function weibull.
    - allows opening results from dynamet projects with read rights only
    - improved feature grouping (low abundant peaks, UPLC data)
    - includes update to use latest hires package 0.0.14
    - requires emzed version 2.24.5 or higher
 

"""

LICENSE = "http://opensource.org/licenses/GPL-3.0"


######################################################################################
#                                                                                    #
# DO NOT TOUCH THE CODE BELOW UNLESS YOU KNOW WHAT YOU DO !!!!                       #
#                                                                                    #
#                                                                                    #
#       _.--""--._                                                                   #
#      /  _    _  \                                                                  #
#   _  ( (_\  /_) )  _                                                               #
#  { \._\   /\   /_./ }                                                              #
#  /_"=-.}______{.-="_\                                                              #
#   _  _.=('""')=._  _                                                               #
#  (_'"_.-"`~~`"-._"'_)                                                              #
#   {_"            "_}                                                               #
#                                                                                    #
######################################################################################


#from dynamet.version import version as VERSION


VERSION_STRING = "%s.%s.%s" % VERSION

ENTRY_POINTS = dict()
ENTRY_POINTS['emzed_package'] = [ "package = " + PKG_NAME, ]
if IS_EXTENSION:
    ENTRY_POINTS['emzed_package'].append("extension = " + PKG_NAME)
if APP_MAIN is not None:
    ENTRY_POINTS['emzed_package'].append("main = %s" % APP_MAIN)


if __name__ == "__main__":   # allows import setup.py for version checking

    from setuptools import setup  # import distutils.config

    def patched(self):
        return dict(realm="pypi",
                    username='pkiefer',
                    password='12karcher@dynamet',
                    repository='http://uweschmitt.info:37614',
                    server="local",
                    )
    # distutils.config.PyPIRCCommand._read_pypirc = patched


    # from setuptools import setup
    setup(name=PKG_NAME,
        packages=[ PKG_NAME ],
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=AUTHOR_URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        version=VERSION_STRING,
        entry_points = ENTRY_POINTS,
	include_package_data = True,
      install_requires=['hires==0.0.14', 'pacer==0.5.3']
        )
   
