import sys
print 'Starting'




def initialize():
    tot_arg =len(sys.argv)
    if tot_arg !=2:
        print 'Please provide only one command!!'
        return
    if sys.argv[1]=='create':
        print 'Create Directory'
        


if __name__ == "__main__":initialize()
