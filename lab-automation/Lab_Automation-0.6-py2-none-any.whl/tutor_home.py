from Tkinter import *
import json
from tutor_tab import assignment, student, marks, question
from instr_ta_tab import stud_pro, ansassign
TITLE_FONT = ("Helvetica", 18, "bold")

class TutorHome(Frame):
	def __init__(self, parent, controller):								#editor window 
		Frame.__init__(self, parent)
		self.controller = controller
		self.frames = {}
		self.array = []
#		self.geometry('500x500')
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=12)
		frame1 = Frame(self)
		frame1.grid(row=0,column=0,sticky="nsew")
		frame2 = Frame(self)
		frame2.grid(row=0,column=1,sticky="nsew")

		for F in (assignment, student, marks, question, stud_pro, ansassign):
			page_name = F.__name__
			fram = F(frame2, self)
			self.frames[page_name] = fram
			fram.grid(row = 0, column = 1, sticky = "nsew")

		but0 = Button (frame1,fg="black",text="Assignment",height="3", command = lambda: self.show_frame("assignment"))
		but0.pack(side = TOP,fill=X)
		but2 = Button (frame1,fg="black",text="Students",height="3", command = lambda: self.show_frame("student"))
		but2.pack(side = TOP,fill=X)
		but3 = Button (frame1,fg="black",text="Marks",height="3", command = lambda: self.show_frame("marks"))
		but3.pack(side = TOP,fill=X)
		# self.show_frame("assignment")

	def show_frame(self, page_name, assignment = "", key = ""):
		frame = self.frames[page_name]
		frame.tkraise()
		if page_name == "assignment":
			self.array = []
		self.array.append(frame)
		if page_name == "assignment" or page_name == "student" or page_name == "marks":
			frame.load()
		if page_name == "question" or page_name == "stud_pro":
			frame.load(assignment)
		if page_name == "ansassign":
			frame.load(assignment, key)

	def load(self, info):
		self.course = info
		self.show_frame("assignment")

	def back(self):
		if(len(self.array) > 1):
			frame = self.array[len(self.array) - 2]
			self.array = self.array[:len(self.array) - 1]
			frame.tkraise()