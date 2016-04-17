
# high level importing to extract whats necessary from your '@cyther' code
import sys
sys.path.insert(0, 'X:\Cyther')
import example_file

# bringing everything into your local namespace
extract_these = ', '.join([name for name in dir(example_file) if not name.startswith('__')])
exec('from example_file import ' + extract_these)

# freshening up your namespace
del example_file
del sys.path[0]
del sys

# this is the end of the setup actions
a = ''.join([str(x) for x in range(10)])
