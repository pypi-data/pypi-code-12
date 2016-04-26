from Tkinter import *
import json
from instructor_tab import assignment, student, marks, question
from instr_ta_tab import stud_pro, ansassign
TITLE_FONT = ("Helvetica", 18, "bold")

class InstructorHome(Frame):
	def __init__(self, parent, controller):								#Displays Course Home of instructor 
		Frame.__init__(self, parent)
		self.controller = controller
		self.frames = {}
		self.array = []
		self.grid_columnconfigure(0,weight=1)
		self.grid_columnconfigure(1,weight=13)
		self.grid_columnconfigure(2,weight=1)
		frame1 = Frame(self)							#Left tab pane frame
		frame1.grid(column=0,row=0,sticky="nsew")
		frame2 = Frame(self)							#Centre frame
		frame2.grid(column=1,row=0,sticky="nsew")
		frame3 = Frame(self)							#Frame with pass keys for students and tutors
		frame3.grid(column=2,row=0,sticky="nsew")
		self.label0 = label0 = Label(frame3, text = "",bd=5)
		label0.grid(row=0, column=0, sticky="nsew")

		for F in (assignment, student, marks, question, stud_pro, ansassign):
			page_name = F.__name__
			fram = F(frame2, self)
			self.frames[page_name] = fram
			fram.grid(row = 1, column = 0, sticky = "nsew")
														#buttons on left frame for assignment,Students and Marks
		but0 = Button (frame1,fg="black",text="Assignment",height="5", command = lambda: self.show_frame("assignment"))
		but0.pack(side = TOP,fill=X)
		but2 = Button (frame1,fg="black",text="Students",height="5", command = lambda: self.show_frame("student"))
		but2.pack(side = TOP,fill=X)
		but3 = Button (frame1,fg="black",text="Marks",height="5", command = lambda: self.show_frame("marks"))
		but3.pack(side = TOP,fill=X)

	def show_frame(self, page_name, assignment = "", key = ""):				#Displays different frame according to different buttons for instructor
		frame = self.frames[page_name]
		frame.tkraise()
		if page_name == "assignment":
			self.array = []
		self.array.append(frame)
		if page_name == "assignment" or page_name == "student" or page_name == "marks":
			frame.load()
		if page_name == "question" or page_name == "stud_pro":
			# print assignment
			frame.load(assignment)
		if page_name == "ansassign":
			frame.load(assignment, key)

	def back(self):										#back button reconfiguration for internal frames
		if(len(self.array) > 1):
			frame = self.array[len(self.array) - 2]
			self.array = self.array[:len(self.array) - 1]
			frame.tkraise()

	def load(self, info):				#loads the right frame
		self.course = info
		response = json.loads((((self.controller)).client).get("http://172.16.115.106:8080/courselist/").content)
		courses = response["courses"]

		for name in courses:
			if name["name"] == info:
				self.label0.config(text=("TA Pass Key: \n" + name["TApasskey"] + "\n Student Pass Key: \n" + name["Studentpasskey"]))
		self.show_frame("assignment")