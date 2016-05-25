#!//usr/bin/env python

# Redirect stdout and stderr to a file
import sys
sys.stdout = open('site_post.out', 'a')
sys.stderr = open('site_post.err', 'a')

import glob
import re
import json
import os
import htcondor


class Test:
    def __init__(self):
        self.starttime = 0
        self.endtime = 0
        self.success = False
        self.duration = 0
        self.cache = ""
    


def main():
    """
    Process all of the output from the sites
    """
    
    site = sys.argv[1]
    
    # First open the logfile
    logfile = open(os.path.join(site, "%s.log" % site))
    
    # Read in the events
    events = htcondor.read_events(logfile)
    
    # Tests is a ClusterId.ProcId indexed dictionary, so we overwrite subsequent
    # events.
    tests = {}
    for event in events:
        tmpTest = Test()
        if 'TriggerEventTypeName' in event and event['TriggerEventTypeName'] == "ULOG_JOB_TERMINATED" and 'Chirp_StashCp_DlTimeMs' in event and event['Chirp_StashCp_DlTimeMs'] != "":
            # A finished event
            
            tmpTest.duration = float(event['Chirp_StashCp_DlTimeMs']) / 1000
            if 'Chirp_TransferSuccess' in event and event['Chirp_TransferSuccess'] == True:
                tmpTest.success = True
                
            if "Chirp_StashCp_Prefix" in event and event["Chirp_StashCp_Prefix"] != "":
                tmpTest.cache = event["Chirp_StashCp_Prefix"]
                
        tests["%i.%i" % (event['Cluster'], event['Proc']) ] = tmpTest.__dict__
    
    
    outputfile = "postprocess.%s.json" % site
    with open(outputfile, 'w') as f:
        f.write(json.dumps(tests.values()))
    
    return 0
                
        

if __name__ == "__main__":
    sys.exit(main())
