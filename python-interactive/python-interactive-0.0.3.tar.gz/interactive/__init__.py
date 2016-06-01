import sys
import code
import cmd

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

class Shell(code.InteractiveConsole):
	"Wrapper around Python that can filter input/output to the shell"
	def __init__(self, locals=None, stdin=None, stdout=None):
		if stdin is None:
			stdin = sys.stdin
		if stdout is None:
			stdout = sys.stdout
		self.stdin = stdin
		self.stdout = stdout
		self.cache = OutputCache()
		code.InteractiveConsole.__init__(self, locals)
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
			more = code.InteractiveConsole.push(self, line)
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

class Console(cmd.Cmd):
	def __init__(self, _in, _out, _locals=None, parent_console=None):
		if _locals is None:
			_locals = {}
		if parent_console is None:
			class InjectParent(cmd.Cmd):
				def __init__(self, _out):
					self.title = "There is no parent menu"
					self.banner = "No banner provided"
					import sys
					self.stdout = _out 
					cmd.Cmd.__init__(self, stdin=_in, stdout=_out)
				def do_title(self, args):
					'''title\nPrints this menu's title'''
					self.write(self.title + '\n')
				def write(self, *args):
					for arg in args:
						self.stdout.write(arg)
			parent_console = InjectParent(_out)
		self.locals = _locals 
		self.prompt = '(DEBUG)> '
		self.parent = parent_console
		self.title = "Debug Console"
		cmd.Cmd.__init__(self, stdin=_in, stdout=_out)
	def do_python(self, args):
		"""python [-c [source]]	
Closely emulate the behavior of the interactive Python interpreter with the
locals set to the main function of the application (app).  You can use it to 
interrogate the application during run time and debug issues on the fly.  

Use the ''-c'' flag to proxy requests into the Python environment one command at
a time
"""
		if args.startswith('-c '):
			args = args[3:]
		else:
			args = ''
		python = Python(self.locals)
		python(args)
	def do_title(self, args):
		"""title\nPrints this menu's title"""
		self.parent.write(self.titlei + '\n')
	def do_quit(self, args):
		"""quit\nReturns to %s %s"""%(self.parent.banner, self.parent.title) 
		return True
	def preloop(self):
		self.parent.write('Entering the %s\n'%self.title)
	def postloop(self):
		self.parent.write('Exiting the %s\n'%self.title)	
	def do_EOF(self, *args):
		"""\nReturns to %s %s"""%(self.parent.banner, self.parent.title) 
		return self.do_quit(args)
	def do_exit(self, *args):
		"""exit\nReturns to %s %s"""%(self.parent.banner, self.parent.title) 
		return self.do_quit(args)
	def do_parent(self, args):
		"""parent [command]
Prints the parent's title or proxies commands to it. 
Requests to proxy either ''quit'' or ''exit'' are ignored.
"""
		if args and args.lower().strip() not in ['quit','exit']:
			self.parent.onecmd(args)
		elif args.lower().strip() in ['quit','exit']:
			self.parent.write('You cannot do that from here!\n')
		else:
			self.parent.onecmd('title')
	def __call__(self, *args):
		self.cmdloop()
	

if __name__ == '__main__':
	import sys
	console = Console(sys.stdin, sys.stdout)
	console.cmdloop()
