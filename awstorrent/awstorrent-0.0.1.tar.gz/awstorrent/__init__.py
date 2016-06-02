#!/usr/bin/python

import time 
import subprocess
import pyperclip
from os import path


# create tmp dir on aws
def download(aws,torrent,title,output_dir,keep_in_aws=False):
    
    #parse torrent file name
    index=torrent.find('.torrent')+8
    torrent_file=torrent[0:index]
    print("torrent file:" ,torrent_file)
    
    cur_path=path.abspath(path.dirname(__file__))
    pem=path.join(cur_path,'icearasi.pem')
    
    subprocess.run(['chmod','400',pem])
    tmpdir="tmpdir%s"%int(time.time()) if title is None else title
    # download with transmission-cli 
    transmission_cmd=["transmission-cli","-D","-f",
      "/home/firearasi/killtransmission","-w",tmpdir,torrent_file]
    ssh_cmd=['ssh','-i',pem,aws]+transmission_cmd
    print("ssh_cmd: ",ssh_cmd)
    ret_code=subprocess.run(ssh_cmd).returncode

    # Copy downloaded dir to local dir
    print("Return code:",ret_code)

    if ret_code==255:
        print("AWS bt download succeeded...")
        print("Copying to local dir:",output_dir)
  
        #Get subdirectory of the tmpdir
        remote_files_tmp=aws+':'+tmpdir
        remote_files=aws+':'+tmpdir+'/\*'
        subprocess.run(['scp','-i','icearasi.pem',
            '-r',remote_files_tmp,output_dir])
    else:
        print("Download failed!")

    if not keep_in_aws:
        subprocess.run(['ssh',aws,'rm',tmpdir,'-rf'])
  




