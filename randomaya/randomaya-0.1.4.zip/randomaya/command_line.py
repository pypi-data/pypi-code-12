
import sys
import randomaya

def main():
    print "entering command center"
    arg = sys.argv[1]
    print arg
    randomaya.getTranslation(arg)
