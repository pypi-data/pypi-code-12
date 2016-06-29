import sys
import runpy

assert(sys.argv[1] == "-m")
sys.argv = sys.argv[2:]
runpy.run_module(sys.argv[0], run_name="__main__", alter_sys=True)
