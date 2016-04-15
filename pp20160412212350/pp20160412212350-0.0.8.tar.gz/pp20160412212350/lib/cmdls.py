def do_ls(args):
    print "Listing", args.file

    import subprocess
    print subprocess.check_output(['ls'] + args.file)
