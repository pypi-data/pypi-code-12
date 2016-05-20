
import os
import sys
import urllib2
from os.path import expanduser
import time


def main():
    if len(sys.argv) < 2:
        print 'usage: sync_iterm_profile REMOTE_URL'
        return
    home = expanduser("~")
    profile_location = home + '/Library/Application Support/iTerm2/DynamicProfiles/mafiasync.prof'
    server_list_url = sys.argv[1]

    while True:
        profile_content = '''{
          "Profiles": [
          PROFILE_ARRAY
          ]
        }'''

        
        content = urllib2.urlopen(server_list_url).read()
        profile_str = ''
        for line in content.split('\n'):
            line = line.strip()
            
            if len(line) != 0:
                parts = line.split(',')
                name = parts[0]
                cmd = parts[1]
                _tags = parts[2].split('|')
                tags = []
                for tag in _tags:
                    tags.append('"' + tag.strip() + '"')
                # print ','.join(tags)
                profile_str += '''   { 
           "Name": "%s",
           "Guid": "%s",
           "Custom Command" : "Yes",
           "Command" : "%s",
           "Tags" : [
              %s
            ],
        },''' % (name, name, cmd, ','.join(tags))

        profile_content = profile_content.replace('PROFILE_ARRAY',profile_str)
        open(profile_location,'w').write(profile_content)
        print 'sleep'
        time.sleep(60)

if __name__ == '__main__':
    main()