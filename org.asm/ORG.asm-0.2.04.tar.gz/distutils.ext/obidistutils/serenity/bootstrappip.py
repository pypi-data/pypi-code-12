'''
Created on 22 janv. 2016

@author: coissac
'''

import sys
from urllib import request
import os.path

from obidistutils.serenity.util import get_serenity_dir
from obidistutils.serenity.rerun import rerun_with_anothe_python
from obidistutils.serenity.checkpython import is_a_virtualenv_python

getpipurl="https://bootstrap.pypa.io/get-pip.py"

def bootstrap():

    getpipfile=os.path.join(get_serenity_dir(),"get-pip.py")
    
    with request.urlopen(getpipurl) as getpip:
        with open(getpipfile,"wb") as out:
            for l in getpip:
                out.write(l)
                
    python = sys.executable
    
    if is_a_virtualenv_python():
        command= "%s %s" % (python,getpipfile)        
    else:
        command= "%s %s --user" % (python,getpipfile)
    
    os.system(command)
    
    rerun_with_anothe_python(python)
    