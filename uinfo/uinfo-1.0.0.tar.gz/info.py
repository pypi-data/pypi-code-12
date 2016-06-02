#!/usr/bin/env python
#A system information gathering Script:pysysinfo.py
import subprocess

#command: uname
def uname_func():
  uname = "uname"
  uname_arg = "-a"
  print("Gathering system information with %s command:\n" % uname) 
  subprocess.call([uname,uname_arg])

#command: df
def disk_func():
  diskspace = "df"
  diskspace_arg = "-h"
  print("\nGathering diskspace information %s command:\n" % diskspace)
  subprocess.call([diskspace,diskspace_arg])  
  #subprocess.call("df -h",shell=True)

def main():
  uname_func()
  disk_func()

if __name__ == "__main__":
  main()
