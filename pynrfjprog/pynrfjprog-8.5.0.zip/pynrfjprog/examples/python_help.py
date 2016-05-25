""" 

    This file contains example code meant to be used in order to test the 
    pynrfjprog API.
    
    Sample program: python_help.py
    
    Run from command line:  
        python python_help.py  
    or if imported as "from pynrfjprog import examples"
        examples.python_help.run()
    
    Program flow:
        0. Python help() is used to list the available API functions

"""

from __future__ import division
from __future__ import print_function

from builtins import int

# Import pynrfjprog API module
from pynrfjprog import API

def run():
    print('# pynrfjprog  python_help  example started...  ')
    print('# Python help() is used to list information regarding the module ')
    
    # Use the python help() to list the available information regarding the API module
    help(API)

    print('# Example done...  ')
    
 
if __name__ == '__main__':
    run()


