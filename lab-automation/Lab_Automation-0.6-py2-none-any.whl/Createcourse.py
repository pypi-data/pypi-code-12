from Tkinter import *
import json
TITLE_FONT = ("Helvetica", 18, "bold")
Text_FONT  = ("Times New Roman", 18, "italic")

class Createcourse(Frame):
	def __init__(self, parent, controller):								#editor window 
		Frame.__init__(self, parent)
		self.controller = controller
#		self.geometry('500x500')
		self.grid_columnconfigure(0,weight=3)
		self.grid_columnconfigure(1,weight=1)
		self.grid_columnconfigure(2,weight=3)
		self.grid_rowconfigure(0,weight=6)
		self.grid_rowconfigure(1,weight=1)
		self.grid_rowconfigure(2,weight=1)
		self.grid_rowconfigure(3,weight=1)
		self.grid_rowconfigure(4,weight=10)
		lab0 = Label(self,text="Course Name: ",font=Text_FONT)
		lab0.grid(row=1,column=1,sticky="nsew")
		self.enter = enter = Entry(self, bd=5,font=Text_FONT)
		enter.grid(row=2,column=1,sticky="nsew")
		reg = Button(self,text="Create",font=Text_FONT, command = lambda: self.regcourse(controller))
		reg.grid(row=3,column=1,sticky="nsew")

	def regcourse(self, controller):
		coursename = self.enter.get()
		response = json.loads(controller.client.get("http://172.16.115.106:8080/courseregister/" , params = {'coursename': coursename}).content)
		# print response
		controller.show_frame("Coursepage")