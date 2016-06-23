from b4msa.command_line import CommandLine
import os
import sys
fname = 'text.json'
c = CommandLine()
sys.argv = ['b4msa', '-k', '2', '-N', '11', fname]
c.main()
