from .cli import Cli
import sys
from terminal import red

class FakeOut:
    def __init__(self):
        self.str=''
        self.n=0
    def write(self,s):
        self.str += str(s)
        self.n+=1
    def result(self):
        return self.str
    def clear(self):
        self.str=''
        self.n=0
    def flush(self):
        pass

def testcmd(arr):

    f = FakeOut()
    old = sys.stdout
    sys.stdout = f

    try:
        Cli().main(arr)
    except Exception as e:
        msg = format(e)
        print(red('\n  ERROR: %s\n' % msg))
        if '()' in msg and 'argument' in msg:
            print(red('  add "-h" for more information\n'))

    sys.stdout = old
    return f.result()