from sys import argv
import cProfile

try:
    module_to_run = argv[1]

    argv = argv[1:]

    exec "from %s import main" % module_to_run

except Exception as e:
    print "Error: %s" % e
    print "usage: 'python -m knxsonos <filename>'"
    print "        the function 'main' in the specified file will be run"

#cProfile.run('main2(argv)', None, 'cumtime')
main()
