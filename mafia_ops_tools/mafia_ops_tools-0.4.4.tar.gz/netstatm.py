import os
import time


def main():
    while True:
        script = "netstat -n|grep ^tcp|awk '{print $NF}'|sort -nr|uniq -c"
        os.system(script)
        time.sleep(1)

if __name__ == '__main__':
    main()