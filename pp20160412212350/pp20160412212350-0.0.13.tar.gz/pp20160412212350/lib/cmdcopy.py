def do_copy(args):
    print "Copying", args.input, args.output

    from shutil import copyfile
    copyfile(args.input, args.output)
