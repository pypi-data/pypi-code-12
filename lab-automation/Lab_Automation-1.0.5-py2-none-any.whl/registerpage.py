from Tkinter import *
import json
TITLE_FONT = ("Helvetica", 18, "bold")
Text_FONT  = ("Times New Roman", 18, "italic")

class Registerpage(Frame):
	def __init__(self, parent, controller):								#Course Registration frame
		Frame.__init__(self, parent)
		self.controller = controller
		self.grid_columnconfigure(0,weight=3)
		self.grid_columnconfigure(1,weight=1)
		self.grid_columnconfigure(2,weight=3)
		self.grid_rowconfigure(0,weight=6)
		self.grid_rowconfigure(1,weight=1)
		self.grid_rowconfigure(2,weight=1)
		self.grid_rowconfigure(3,weight=1)
		self.grid_rowconfigure(4,weight=10)
		lab0 = Label(self,text="Pass Key: ",font=Text_FONT)
		lab0.grid(row=1,column=1,sticky="nsew")
		self.enter = enter = Entry(self, bd=5,font=Text_FONT)		#entry box for passkey
		enter.grid(row=2,column=1,sticky="nsew")
		reg = Button(self,text="Register", command = lambda: self.joincourse(controller),font=Text_FONT)
		reg.grid(row=3,column=1,sticky="nsew")

	def joincourse(self, controller):									#takes passkey entered by student/tutor to register them to the course
		passkey = self.enter.get()
		if controller.usertype == "Tutor":
			response = json.loads(controller.client.get("http://172.16.115.106:8080/courseregister/" , params = {'TApasskey': passkey}).content)
		else:
			response = json.loads(controller.client.get("http://172.16.115.106:8080/courseregister/" , params = {'Studentpasskey': passkey}).content)
		controller.show_frame("Coursepage")