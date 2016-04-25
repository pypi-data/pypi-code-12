from Tkinter import *
import json
from functools import partial
TITLE_FONT = ("Helvetica", 18, "bold")
text_font = ("Times New Roman", 15, "italic")
text1_font = ("Times New Roman", 15, "bold")

class Coursepage(Frame):
	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

	def load(self, controller):
		courses = json.loads(controller.client.get("http://172.16.115.106:8080/courselist/").content)
		# print courses["courses"]
		# courses = {"courses": [{"name": "Abc"}]}
		users = courses["courses"]
		for child in self.winfo_children():
			child.destroy()
		for name in users:
			if controller.usertype == "Instructor":
				coursebutton = Button(self,text=name["name"],width = 50,height = 2,font=text_font, command = partial(controller.show_frame, "InstructorHome", name["name"]))						#Prints course names from list as buttons
			elif controller.usertype == "Tutor":
				coursebutton = Button(self, text=name["name"],width = 50,height = 2,font=text_font, command = partial(controller.show_frame, "TutorHome", name["name"]))
			else:
				coursebutton = Button(self, text=name["name"],width = 50,height = 2,font=text_font, command = partial(controller.show_frame, "StudentHome", name["name"]))
			coursebutton.pack(side = TOP,pady=3)
		if controller.usertype == "Instructor":
			newcourse = Button(self,text="Create Course",font=text1_font,command = lambda: controller.show_frame("Createcourse"))
			newcourse.pack(side=TOP,pady=3)
		else:
			joincourse = Button(self,text="Join Course",font=text1_font, command = lambda: controller.show_frame("Registerpage"))
			joincourse.pack(side=TOP,pady=3)