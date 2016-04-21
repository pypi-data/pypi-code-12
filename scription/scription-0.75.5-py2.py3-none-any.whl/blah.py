from scription import *
import sys

@Command(
        test=Spec('does this get removed?', OPTION, remove=True),
        )
@Alias('blah.py')
def blah(test):
    if test not in sys.argv:
        print('success!')
    else:
        print('failure')

Main()
