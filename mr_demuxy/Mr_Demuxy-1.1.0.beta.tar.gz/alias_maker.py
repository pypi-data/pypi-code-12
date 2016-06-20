


#!/usr/bin/python

from __future__ import division

import site
import os
import subprocess
import sys
import argparse

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser()
parser.add_argument('--zcluster', action='store_true')
args = parser.parse_args()



def main():

    user_home = os.path.expanduser('~')
    user_path = site.USER_BASE
    mr_path = os.path.join(user_home, '.mr_bash')
    export_line = 'export PATH=' + user_path + ':$PATH'

    try:
        import Mr_Demuxy
        mr_demuxy_dir = os.path.dirname(Mr_Demuxy.__file__)
        pe_alias = 'alias pe_demuxer=\"python ' + mr_demuxy_dir + '/pe_demuxer_dist.py\"'
        merg_alias = 'alias merged_demuxer=\"python ' + mr_demuxy_dir + '/merged_demuxer_dist.py\"'

        if args.zcluster is True:
           correct_pypath = 'export PATH=/usr/local/python/2.7.2/bin/python:$PATH'
           correct_python = 'alias python=\"/usr/local/python/2.7.2/bin/python\"'
           bash_profile_stuff(
            user_home,
            export_line,
            pe_alias, 
            merg_alias,
            correct_pypath,
            correct_python
            )
        else:
            bash_profile_stuff(user_home, export_line, pe_alias, merg_alias)

        

        
    
    except ImportError:
        bash_profile_stuff(user_home, export_line, pe_alias, merg_alias)
        print('\nSo, the local install dir wasnt in the PATH, which this script tried to fix.\n\n\
Try closing terminal and re-running this script again. It should hopefully work\n')
        sys.exit(1)



def bash_checker(in_file, line_want):
    append_file = True
    for line in in_file:
        if line_want in line:
            append_file = False
            break
            
        if line_want not in line:
            append_file = True
    return append_file

def bash_profile_stuff(user_home, export_line, alias1, alias2, pypath=None, pyalias=None):
    
    bash_file = os.path.join(user_home, '.bash_profile')
    #bash_file = os.path.join(user_home, want_bash)
    

    try:
        open_bf = open(bash_file)
        local_pypath = bash_checker(open_bf, export_line)
        mr_demuxer_alias1 = bash_checker(open_bf, alias1)
        mr_demuxer_alias2 = bash_checker(open_bf, alias2)
        if args.zcluster is True:
            pypath_check = bash_checker(open_bf, pypath)
            pyalias_check = bash_checker(open_bf, pyalias)
        
        open_bf.close()

        with open(bash_file, 'a') as bf_ap:
            if local_pypath is True:
                bf_ap.write(
                    '\n#Added by Mr. Demuxy\n'
                     + export_line
                    )
            if mr_demuxer_alias1 is True:
                bf_ap.write(
                    '\n' + alias1)
            if mr_demuxer_alias1 is True:
                bf_ap.write(
                    '\n' + alias2)
            if pypath is not None:
                if pypath_check is True:
                    bf_ap.write(
                        '\n#Python 2.7.2 Zcluster stuff\n'
                        + pypath + '\n'
                        )
                
            if pyalias is not None:
                if pyalias_check is True:
                    bf_ap.write(
                        pyalias)

               


    except IOError:
        with open(bash_file, 'w+') as f:
            f.write(
                '\n#Added by Mr. Demuxy\n'
                 + export_line + '\n'
                 + alias1 + '\n' 
                 + alias2 + '\n'
                 + pypath + '\n'
                 + pyalias + '\n'
                 )

    
if __name__ == '__main__':
    main()


    


    



