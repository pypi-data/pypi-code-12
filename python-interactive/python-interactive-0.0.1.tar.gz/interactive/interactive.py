import sys
from code import InteractiveConsole 

class OutputCache:
	"Cache the out text so we can analyze it before returning it"
	def __init__(self): 
		self.reset()
	def reset(self): 
		self.out = []
	def write(self,line): 
		self.out.append(line)
	def flush(self):
		output = ''.join(self.out)
		self.reset()
		return output

class Shell(InteractiveConsole):
	"Wrapper around Python that can filter input/output to the shell"
	def __init__(self, locals=None, stdin=None, stdout=None):
		if stdin is None:
			stdin = sys.stdin
		if stdout is None:
			stdout = sys.stdout
		self.stdin = stdin
		self.stdout = stdout
		self.cache = OutputCache()
		InteractiveConsole.__init__(self, locals)
		return
	def take_output(self): 
		sys.stdout = self.cache
		self.stderr = sys.stderr
		sys.stderr = self.cache
	def return_output(self): 
		sys.stdout = self.stdout
		sys.stderr = self.stderr
	def push(self, line):
		try:
			self.take_output()
			# you can filter input here by doing something like
			# line = filter(line)
			if line.strip() == 'exit()':
				raise SystemExit()
			more = InteractiveConsole.push(self, line)
		finally:
			self.return_output()
		output = self.cache.flush()
		# you can filter the output here by doing something like
		# output = filter(output)
		#print [ord(c) for c in output]
		if output:
			print>>self.stdout, output, # or do something else with it
		return more  
	def raw_input(self, prompt=None):
		if self.stdin == sys.stdin and self.stdout == sys.stdout:
			return raw_input(prompt)
		elif prompt is not None:
			self.stdout.write(prompt)
		input = self.stdin.readline()
		if not input:
			raise EOFError()
		return input.rstrip('\r\n')

class Python:
	def __init__(self, locals=None, stdin=None, stdout=None):
		if stdin is None:
			stdin = sys.stdin
		if stdout is None:
			stdout = sys.stdout
		self.stdin = stdin
		self.stdout = stdout
		self.locals = locals
	def __call__(self, *args):
		sh = Shell(self.locals, self.stdin, self.stdout)
		saved_locals = dict((a,b) for a,b in sh.locals.iteritems())
		args = ' '.join(arg for arg in args)
		if args:
			sh.runcode(args)
		else:
			banner = '''
Entering a Python interactive shell
Use exit() or Ctrl-D (i.e. EOF) to exit
'''
			self.stdout.write(banner)
			try:
				sh.interact(banner='')
			except EOFError:
				self.stdout.write('\nExiting the Python interactive shell\n\n')
			except SystemExit:
				self.stdout.write('\nExiting the Python interactive shell\n\n')
			except Exception, e:
				print e
		return

if __name__ == '__main__':
	import sys
	argv = []
	if len(sys.argv) > 1:
		argv = sys.argv[1:]
	python = Python()
	python(*(arg for arg in argv))
