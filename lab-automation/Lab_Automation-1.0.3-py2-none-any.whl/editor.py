from Tkinter import *
import ScrolledText
import tkFileDialog
import tkMessageBox
import subprocess
import getpass
TITLE_FONT = ("Helvetica", 18, "bold")
text_font = ("Times NEw Roman", 15)

class CodeEditor(Frame):
	def __init__(self, parent, controller):								#editor window 
		Frame.__init__(self, parent)
		self.controller = controller
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)
		self.frame = frame = Frame(self)
		frame.pack(fill=X, side=TOP)
		frame.grid_columnconfigure(0,weight=1)							#column division of frame
		frame.grid_columnconfigure(1,weight=1)
		frame.grid_rowconfigure(0,weight=5)								#row division of frame
		frame.grid_rowconfigure(1,weight=5)
		frame.grid_rowconfigure(2,weight=1)
		#scrolled text input for writing code
		self.code = writepad = ScrolledText.ScrolledText(frame,height=30,font=text_font)
		but1 = Button(self.frame, fg = "red", text = "Compile and Run", height = "1", command = lambda: self.compile())
		frame.grid(row=0,column=0,sticky="nsew")
		writepad.insert(INSERT, "")
		writepad.grid(row=0,column=0,rowspan=2,sticky="nsew",padx=5,pady=5)
		but1.grid(row=2,column=1,sticky="nsew",padx=5,pady=5)
		#scrolled text input for writing test case
		self.inp = writepad1 = ScrolledText.ScrolledText(frame,height=15,font=text_font)
		writepad1.insert(INSERT, "")
		writepad1.grid(row=0,column=1,sticky="nsew",padx=5,pady=5)
		#scrolled text box for writing output after running
		self.out = writepad2 = ScrolledText.ScrolledText(frame,height=15,font=text_font)
		writepad2.insert(INSERT, "")
		writepad2.grid(row=1,column=1,sticky="nsew",padx=5,pady=5)

		#compile function of the written code
	def compile(self):
		code = self.code.get("1.0", END)[:-1]
		inp = self.inp.get("1.0", END)[:-1]
		file_code = "/home/" + getpass.getuser() + "/.project/" + "test" + ".c"					#saves code in file
		with open(file_code, 'w') as f:
			f.write(code)
			f.close()
		inp_file = "/home/" + getpass.getuser() + "/.project/" + "test" + ".in"
		with open(inp_file, 'w') as f:
			f.write(inp)
			f.close()
		self.out.delete("1.0", END)
		try:
			subprocess.check_output("gcc " + file_code + " -o " + file_code[:-2], shell = True, stderr = subprocess.STDOUT)
			response = subprocess.check_output(file_code[:-2] + " < " + inp_file, shell = True)
		except Exception as e:
			response = e.output
			response = response[1 + len(file_code):]
		self.out.insert(INSERT, response)