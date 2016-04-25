from Tkinter import *
import json
from editor import CodeEditor
from student_tab import assignment, stud_pro, answer
TITLE_FONT = ("Helvetica", 18, "bold")

class StudentHome(Frame):
	def __init__(self, parent, controller):								#editor window 
		Frame.__init__(self, parent)
		self.array = []
		self.controller = controller
		self.frames = {}
#		self.geometry('500x500')
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=11)
		frame1 = Frame(self)
		frame1.grid(row=0,column=0,sticky="nsew")
		frame2 = Frame(self)
		frame2.grid(row=0,column=1,sticky="nsew")

		for F in (assignment, stud_pro, answer):
			page_name = F.__name__
			fram = F(frame2, self)
			self.frames[page_name] = fram
			fram.grid(row = 0, column = 1, sticky = "nsew")
		# frame1.grid_columnconfigure(0,weight=1)
		but0 = Button (frame1,fg="black",text="Assignment",height="5", command = lambda: self.show_frame("assignment"))
		but0.pack(side=TOP,fill=X)#grid(row=0,column=0,sticky="nsew",padx=4)
		but1 = Button (frame1,fg="black",text="Profile",height="5", command = lambda: self.show_frame("stud_pro"))
		but1.pack(side=TOP,fill=X)#grid(row=1,column=0,sticky="nsew",padx=4)

	def show_frame(self, page_name, assign = ""):
		frame = self.frames[page_name]
		frame.tkraise()
		if page_name == "assignment":
			self.array = []
		self.array.append(frame)
		if page_name == "assignment" or page_name == "stud_pro":
			frame.load()
		if page_name == "answer":
			frame.load(assign)

	def back(self):
		if(len(self.array) > 1):
			frame = self.array[len(self.array) - 2]
			self.array = self.array[:len(self.array) - 1]
			frame.tkraise()

	def load(self, info):
		self.course = info
		self.show_frame("assignment")