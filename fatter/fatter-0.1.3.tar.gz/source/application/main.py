
import fatter
import fatter.application

import io
import sys
import pickle
from math import sin, cos, pi
try:
	import Tkinter as TK
	import tkFileDialog
	import tkMessageBox
except ImportError:  # Python 3.
	try:
		import tkinter as TK
		import tkinter.filedialog as tkFileDialog
		import tkinter.messagebox as tkMessageBox
	except ImportError:
		raise ImportError('Tkinter not available.')

try:
	import ttk as TTK
except ImportError:  # Python 3.
	try:
		from tkinter import ttk as TTK
	except ImportError:
		raise ImportError('Ttk not available.')

if sys.version_info >= (3, 0):
	StringType = str
	IntegerType = (int,)
	FileType = io.TextIOWrapper
else:
	# In Python 2.x an integer can be an int or long (Python automatically switches to longs when required).
	StringType = str
	IntegerType = (int, long)
	FileType = file


if sys.platform in ['darwin']:
	COMMAND = {
		'new': 'Command+N',
		'open': 'Command+O',
		'save': 'Command+S',
		'close': 'Command+W',
		}
	COMMAND_KEY = {
		'new': '<Command-n>',
		'open': '<Command-o>',
		'save': '<Command-s>',
		'close': '<Command-w>',
		}
else:
	COMMAND = {
		'new': 'Ctrl+N',
		'open': 'Ctrl+O',
		'save': 'Ctrl+S',
		'close': 'Ctrl+W',
		}
	COMMAND_KEY = {
		'new': '<Control-n>',
		'open': '<Control-o>',
		'save': '<Control-s>',
		'close': '<Control-w>',
		}

def valid_num_sides(value):
	try:
		if int(value) < 3:
			raise ValueError
		return True
	except ValueError:
		tkMessageBox.showerror('Invalid number of sides', 'Number of sides must be an integer >= 3.')
		return False

class Vertex(object):
	def __init__(self, canvas, position, num_sides):
		self.canvas = canvas
		self.position = position
		self.num_sides = num_sides
		n, r, r2, r3 = self.num_sides, 3*self.num_sides, 3*self.num_sides, 3*self.num_sides+5
		self.r = r
		self.edges = [
			Edge(self.canvas, [
				(self.position[0] + r2*cos(i * 2 * pi / n), self.position[1] + r2*sin(i * 2 * pi / n)),
				(self.position[0] + r3*cos(i * 2 * pi / n), self.position[1] + r3*sin(i * 2 * pi / n))
				])
			for i in range(self.num_sides)
			]
		self.drawn = self.canvas.create_oval(
			[p + scale*r for scale in [-1, 1] for p in self.position],
			outline='black', fill='grey', tag='vertex'
			)
	def contains(self, point):
		return (point[0] - self.position[0])**2 + (point[1] - self.position[1])**2 <= self.r**2

class Edge(object):
	def __init__(self, canvas, positions):
		self.canvas = canvas
		self.positions = list(positions)
		self.r = 5
		self.drawn = self.canvas.create_line(
				[c for v in self.positions for c in v],
				width=3,
				fill='black',
				smooth=True,
				tag='path'
			)
		self.head = self.canvas.create_oval(
			[p + scale*self.r for scale in [-1, 1] for p in self.positions[-1]],
			outline='black', fill='red', tag='head'
			)
		self.connected_to = None
	def head_contains(self, point):
		return (point[0] - self.positions[-1][0])**2 + (point[1] - self.positions[-1][1])**2 <= self.r**2
	def connect(self, other):
		if other is None:
			if self.connected_to is not None:
				self.canvas.itemconfig(self.connected_to.head, fill='red')
				self.connected_to.connected_to = None
			self.canvas.itemconfig(self.head, fill='red')
			self.connected_to = None
		else:
			assert(other.connected_to is None or other.connected_to == self)
			self.connected_to = other
			self.connected_to.connected_to = self
			self.canvas.itemconfig(self.connected_to.head, fill='blue')
			self.canvas.itemconfig(self.head, fill='blue')
	def redraw(self):
		self.canvas.coords(self.drawn, *[c for v in self.positions for c in v])
		self.canvas.coords(self.head, *[p + scale*self.r for scale in [-1, 1] for p in self.positions[-1]])
		self.canvas.tag_raise('path')
		self.canvas.tag_raise('head')

class FatterApplication(object):
	def __init__(self, parent):
		self.parent = parent
		self.vertices = []
		self.edges = []
		
		self.frame_draw = TK.Frame(self.parent)
		# This needs takefocus set so that we can tell if it has been selected.
		self.canvas = TK.Canvas(self.frame_draw, bg='#dcecff', takefocus=True)
		self.canvas.pack(padx=6, pady=6, fill='both', expand=True)
		self.canvas.bind('<Button-1>', self.canvas_left_click)
		self.canvas.bind('<Double-Button-1>', self.canvas_double_left_click)
		self.canvas.bind('<B1-Motion>', self.canvas_left_move)
		self.canvas.bind('<ButtonRelease-1>', self.canvas_left_release)
		self.canvas.bind('<Button-3>', self.canvas_right_click)
		
		self.frame_draw.pack(fill='both', expand=True)
		self.selected_object = None
		
		# Create the menus.
		self.menubar = TK.Menu(self.parent)
		self.filemenu = TK.Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label='New', command=self.initialise, accelerator=COMMAND['new'])
		self.filemenu.add_command(label='Open...', command=self.load, accelerator=COMMAND['open'])
		self.filemenu.add_command(label='Save...', command=self.save, accelerator=COMMAND['save'])
		self.filemenu.add_separator()
		self.filemenu.add_command(label='Exit', command=self.quit, accelerator=COMMAND['close'])
		self.menubar.add_cascade(label='File', menu=self.filemenu)
		
		self.helpmenu = TK.Menu(self.menubar, tearoff=0)
		self.helpmenu.add_command(label='Help', command=self.show_help, accelerator='F1')
		self.helpmenu.add_separator()
		self.helpmenu.add_command(label='About', command=self.show_about)
		self.menubar.add_cascade(label='Help', menu=self.helpmenu)
		
		self.parent.config(menu=self.menubar)
		
		# Create keyboard shortcuts.
		self.parent.bind(COMMAND_KEY['new'], lambda event: self.initialise())
		self.parent.bind(COMMAND_KEY['open'], lambda event: self.load())
		self.parent.bind(COMMAND_KEY['save'], lambda event: self.save())
		self.parent.bind(COMMAND_KEY['close'], lambda event: self.quit())
		
		self.parent.protocol('WM_DELETE_WINDOW', self.quit)
		
		self.unsaved_word = False
		self.output = None
	
	def initialise(self):
		if self.unsaved_work:
			result = tkMessageBox.showwarning('Unsaved work', 'Save before unsaved work is lost?', type='yesnocancel')
			if (result == 'yes' and not self.save()) or result == 'cancel':
				return False
		
		self.selected_object = None
		self.vertices = []
		self.edges = []
		self.canvas.delete('all')
		
		self.unsaved_work = False
		return True
	def load(self, load_from=None):
		try:
			if load_from is None:
				file_path = tkFileDialog.askopenfilename(
					defaultextension='.ftt',
					filetypes=[('fatter files', '.ftt'), ('all files', '.*')],
					title='Open Fatter File')
				if not file_path:  # Cancelled the dialog.
					return
				try:
					string_contents = open(file_path, 'rb').read()
				except IOError:
					raise ValueError('Error 101: Cannot read contents of %s.' % load_from)
			elif isinstance(load_from, FileType):
				string_contents = load_from.read()
			elif isinstance(load_from, StringType):
				try:
					string_contents = open(load_from, 'rb').read()
				except IOError:
					string_contents = load_from
			else:
				raise ValueError('Error 102: Cannot load from something other than a string or file.')
			
			try:
				spec, version, data = pickle.loads(string_contents)
			except (EOFError, AttributeError, KeyError):
				raise ValueError('Error 103: Cannot depickle information provided.')
			except ValueError:
				raise ValueError('Error 104: Invalid depickle.')
			
			if version != fatter.__version__:
				raise ValueError('Error 105: This file was created in an older version of fatter (%s)' % version)
			
			if spec != 'A fatter file.':
				raise ValueError('Error 108: Invalid specification.')
			
			[vertices, edges] = data
			
			self.vertices = [Vertex(self.canvas, position, num_sides) for position, num_sides in vertices]
			self.edges = [edge for vertex in self.vertices for edge in vertex.edges]
			for edge, (positions, connected_to) in zip(self.edges, edges):
				edge.positions = positions
				if connected_to is not None:
					edge.connect(self.edges[connected_to])
				edge.redraw()
		except (IndexError, ValueError) as error:
			tkMessageBox.showerror('Load Error', error.message)
		
		self.unsaved_work = False
		pass
	def save(self):
		path = tkFileDialog.asksaveasfilename(defaultextension='.ftt', filetypes=[('fatter files', '.ftt'), ('all files', '.*')], title='Save Fatter File')
		if path != '':
			try:
				spec = 'A fatter file.'
				version = fatter.__version__
				vertices = [(vertex.position, vertex.num_sides) for vertex in self.vertices]
				edges = [(edge.positions, None if edge.connected_to is None else self.edges.index(edge.connected_to)) for edge in self.edges]
				data = (vertices, edges)
				pickled_objects = pickle.dumps((spec, version, data))
				with open(path, 'wb') as myfile:
					myfile.write(pickled_objects)
				self.unsaved_work = False
				return True
			except IOError:
				tkMessageBox.showwarning('Save Error', 'Could not open: %s' % path)
	def quit(self):
		# Write down our current state for output. If we are incomplete then this is just None.
		self.output = self.construct_fatgraph()
		
		if self.initialise():
			# Apparantly there are some problems with comboboxes, see:
			#  http://stackoverflow.com/questions/15448914/python-tkinter-ttk-combobox-throws-exception-on-quit
			self.parent.eval('::ttk::CancelRepeat')
			self.parent.destroy()
			self.parent.quit()
	def show_help(self):
		tkMessageBox.showinfo('Help', 'Double click to place vertices. Drag nodes together to create edges.')
		return
	def show_about(self):
		tkMessageBox.showinfo('About', 'fatter (Version %s).\nCopyright (c) Mark Bell 2016.' % fatter.__version__)
	
	def canvas_left_click(self, event):
		self.canvas.focus_set()
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		
		potential = [edge for edge in self.edges if edge.head_contains((x, y))]
		if potential:
			edge = min(potential, key=lambda e: len(e.positions))
			if edge.connected_to is not None:
				for i in range(min(len(edge.connected_to.positions) - 2, 3)):
					edge.connected_to.positions.pop()
				edge.connected_to.redraw()
				edge.connect(None)
				self.unsaved_work = True
			self.selected_object = edge
	def canvas_double_left_click(self, event):
		self.canvas.focus_set()
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		
		if all(not vertex.contains((x, y)) for vertex in self.vertices):
			num_sides = fatter.application.get_input('New vertex', 'Number of sides:', validate=valid_num_sides, default='3')
			if num_sides is not None:
				self.vertices.append(Vertex(self.canvas, (x, y), int(num_sides)))
				self.edges.extend(self.vertices[-1].edges)
				self.unsaved_work = True
		
	def canvas_left_move(self, event):
		self.canvas.focus_set()
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		if self.selected_object is not None:
			edge = self.selected_object
			r = edge.r
			if (x - edge.positions[-1][0])**2 + (y - edge.positions[-1][1])**2 > 3 * r**2:
				for other in self.edges:
					if other != edge and other.connected_to is None:
						if other.head_contains((x, y)):
							# Bolt edges together.
							edge.positions.append(other.positions[-1])
							edge.connect(other)
							self.selected_object = None
							break
				else:
					for i in range(2, len(edge.positions)-1):
						if (x - edge.positions[i][0])**2 + (y - edge.positions[i][1])**2 < r**2:
							edge.positions = edge.positions[:i]
							break
					else:
						edge.positions.append((x, y))
				edge.redraw()
				self.unsaved_work = True
	def canvas_left_release(self, event):
		self.selected_object = None
	def canvas_right_click(self, event):
		self.canvas.focus_set()
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		
		pass
	
	def construct_fatgraph(self):
		labels = dict()
		counter = 0
		for vertex in self.vertices:
			for edge in vertex.edges:
				if edge not in labels:
					labels[edge] = counter
					if edge.connected_to is not None:
						labels[edge.connected_to] = ~counter
					counter += 1
		
		return fatter.FatGraph(tuple(tuple(labels[edge] for edge in vertex.edges) for vertex in self.vertices))


def start(load_from=None):
	root = TK.Tk()
	root.title('fatter')
	fatter_application = FatterApplication(root)
	root.minsize(300, 300)
	root.geometry('700x500')
	root.wait_visibility(root)
	if load_from is not None: fatter_application.load(load_from=load_from)
	root.mainloop()
	return fatter_application.output

if __name__ == '__main__':
	start()

