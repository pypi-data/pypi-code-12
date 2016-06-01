import cmd

from interactive import Python

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
