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
# 		frame = Frame(self)
# 		frame.pack(fill=X, side = TOP)
# 		but2 = Button(frame, fg="red",text="Question 1", height="1")	
# 		but2.pack(side=LEFT)
# 		but3 = Button(frame, fg="red",text="Question 2", height="1")	
# 		but3.pack(side=LEFT)
# 		but4 = Button(frame, fg="red",text="Question 3", height="1")	
# 		but4.pack(side=LEFT)
# #		self.geometry('500x500')
# 		frame1 = Frame(self)
# 		writepad = self.writepad = ScrolledText.ScrolledText(frame1,height=30)
# 		but0 = Button(frame1, fg="red",text="Save", height="1",command=lambda: self.save_command())
# 		but1 = Button(frame1, fg="red",text="Compile", height="1",command=lambda: self.compile())
# 		frame1.pack(side = RIGHT)
# 		writepad.insert(INSERT, "")
# 		writepad.pack(side=TOP)
# 		but1.pack(side=RIGHT)
# 		but0.pack(side=RIGHT)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)
		self.frame = frame = Frame(self)
		frame.pack(fill=X, side=TOP)
		# self.grid_rowconfigure(0, weight = 1)
		# self.grid_columnconfigure(0, weight=1)
		# but.pack(side=LEFT)
		# qee = Label(self.frames[i], text = quest[i])
		# qee.pack(side=LEFT)
		frame.grid_columnconfigure(0,weight=1)
		frame.grid_columnconfigure(1,weight=1)
		frame.grid_rowconfigure(0,weight=5)
		frame.grid_rowconfigure(1,weight=5)
		frame.grid_rowconfigure(2,weight=1)
		self.code = writepad = ScrolledText.ScrolledText(frame,height=30,font=text_font)
		but1 = Button(self.frame, fg = "red", text = "Compile and Run", height = "1", command = lambda: self.compile())
		frame.grid(row=0,column=0,sticky="nsew")
		writepad.insert(INSERT, "")
		writepad.grid(row=0,column=0,rowspan=2,sticky="nsew",padx=5,pady=5)
		but1.grid(row=2,column=1,sticky="nsew",padx=5,pady=5)
		self.inp = writepad1 = ScrolledText.ScrolledText(frame,height=15,font=text_font)
		writepad1.insert(INSERT, "")
		writepad1.grid(row=0,column=1,sticky="nsew",padx=5,pady=5)
		self.out = writepad2 = ScrolledText.ScrolledText(frame,height=15,font=text_font)
		writepad2.insert(INSERT, "")
		writepad2.grid(row=1,column=1,sticky="nsew",padx=5,pady=5)

	def compile(self):
		code = self.code.get("1.0", END)[:-1]
		inp = self.inp.get("1.0", END)[:-1]
		file_code = "/home/" + getpass.getuser() + "/.project/" + "test" + ".c"
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