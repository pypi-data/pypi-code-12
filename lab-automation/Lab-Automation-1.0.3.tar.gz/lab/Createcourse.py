from Tkinter import *
import json
TITLE_FONT = ("Helvetica", 18, "bold")
Text_FONT  = ("Times New Roman", 18, "italic")

class Createcourse(Frame):
	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller
		self.grid_columnconfigure(0,weight=3)
		self.grid_columnconfigure(1,weight=1)			#division of frame into columns
		self.grid_columnconfigure(2,weight=3)
		self.grid_rowconfigure(0,weight=6)
		self.grid_rowconfigure(1,weight=1)			#division of frame into rows
		self.grid_rowconfigure(2,weight=1)
		self.grid_rowconfigure(3,weight=1)
		self.grid_rowconfigure(4,weight=10)
		lab0 = Label(self,text="Course Name: ",font=Text_FONT)
		lab0.grid(row=1,column=1,sticky="nsew")
		self.enter = enter = Entry(self, bd=5,font=Text_FONT)			#Entry for new course name
		enter.grid(row=2,column=1,sticky="nsew")
		reg = Button(self,text="Create",font=Text_FONT, command = lambda: self.regcourse(controller))
		reg.grid(row=3,column=1,sticky="nsew")

	def regcourse(self, controller):					#creates the course for the Instructor 
		coursename = self.enter.get()
		response = json.loads(controller.client.get("http://172.16.115.106:8080/courseregister/" , params = {'coursename': coursename}).content)
		#the above line gets response from the server as to the names of course the user is registeered in
		controller.show_frame("Coursepage")