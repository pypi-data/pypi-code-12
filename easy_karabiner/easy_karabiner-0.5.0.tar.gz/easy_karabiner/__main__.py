# Used for test purpose
if __name__ == '__main__':
    import os
    import sys
    from easy_karabiner.main import *

    args_num = len(sys.argv) - 1

    if args_num == 0:
        inpath = os.path.join(os.path.dirname(__file__), '..', 'samples/test.py')
    else:
        inpath = sys.argv[1]

    if args_num >= 2:
        outpath = sys.argv[2]
        string = False
    else:
        outpath = None
        string = True

    try:
        main.callback(inpath, outpath, verbose=True, string=string)
    except SystemExit as e:
        print(e.code)
