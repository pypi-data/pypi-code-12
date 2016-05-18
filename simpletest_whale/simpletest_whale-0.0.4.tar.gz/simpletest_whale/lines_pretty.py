import argparse

def hello():
    '''
    this is a hello py
    '''

    return "hello"

def get_parser():
    parser = argparse.ArgumentParser(description='a test from whale')
    parser.add_argument('-a','--all', help = 'print 10 times the hellos',\
            action='store_true')
    parser.add_argument('welcome', type=str, nargs='*', help='repeat')
    parser.add_argument('-v','--version', help='displays the current version',\
            action='store_true')
    args = parser.parse_args()
    if args.welcome:
        print (i for i in args.welcome)
    return parser    

def run_command_line():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return
    if args['all']:
        print(hello()*10)
    return 
    

if __name__=='__main__':
    run_command_line()
