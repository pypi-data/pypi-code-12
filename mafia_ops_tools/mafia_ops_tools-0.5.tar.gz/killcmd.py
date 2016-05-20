import os
import sys

def main():
    if len(sys.argv) < 2:
        print 'usage: killcmd CMD'
        return

    command_name = sys.argv[1]
    script = "ps aux | grep '{cmd}' | awk '{print $2}'  | xargs kill -9"
    script = script.replace('{cmd}', command_name)

    os.system(script)

if __name__ == '__main__':
    main()