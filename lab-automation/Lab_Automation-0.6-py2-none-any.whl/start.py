from Tkinter import *
from mainwindow import MainWindow
from login import Login
from signup import SignUp
from editor import CodeEditor
from topframe import TopFrame
from student_home import StudentHome
from tutor_home import TutorHome
from coursepage import Coursepage
from instructor_home import InstructorHome
from registerpage import Registerpage
from Createcourse import Createcourse
import requests
import os
import getpass

class SampleApp(Tk):																#class(SampleApp) has been taken from Stackoverflow.com (under MIT License) from the link http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
	def __init__(self, *args, **kwargs):											#class for calling other windows
		Tk.__init__(self, *args, **kwargs)
		self.array = []
		# self.config(bd=0)
		self.client = requests.session()
		self.usertype = ""
		prowork = "/home/" + getpass.getuser() + "/.project"
		if not os.path.exists(prowork):
			os.makedirs(prowork)
		container = Frame(self, width=1000, height=5000)
		container.pack(fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_rowconfigure(1, weight = 10)
		container.grid_columnconfigure(0, weight=1)

		self.topframe = frame0 = TopFrame(container, self)
		frame0.grid(row=0, column = 0, sticky = "nsew")
		# frame0.pack(fill = X)
		frame0.tkraise()

		self.frames = {}
		for F in (MainWindow, Login, SignUp, Registerpage, Createcourse, CodeEditor, TutorHome, InstructorHome, StudentHome, Coursepage):
			page_name = F.__name__
			frame = F(container, self)
			# frame.config(bd=10)
			self.frames[page_name] = frame

			# put all of the pages in the same location;
			# the one on the top of the stacking order
			# will be the one that is visible.
			frame.grid(row=1, column=0, sticky="nsew")

		self.show_frame("MainWindow")

	def show_frame(self, page_name, info = ""):												#calls other windows to be shown in the same frame
		'''Show a frame for the given page name'''
		if(page_name == "MainWindow"):
			self.array = []
		frame = self.frames[page_name]
		self.array.append(frame)
		frame.tkraise()
		if page_name == "Coursepage":
			frame.load(self)
		if page_name == "InstructorHome" or page_name == "StudentHome" or page_name == "TutorHome":
			frame.load(info)

	def back(self):
		if self.array[len(self.array) - 1] == self.frames["InstructorHome"] and len(self.frames["InstructorHome"].array) > 1:
			self.frames["InstructorHome"].back()
		elif self.array[len(self.array) - 1] == self.frames["StudentHome"] and len(self.frames["StudentHome"].array) > 1:
			self.frames["StudentHome"].back()
		elif self.array[len(self.array) - 1] == self.frames["TutorHome"] and len(self.frames["TutorHome"].array) > 1:
			self.frames["TutorHome"].back()
		elif(len(self.array) > 1):
			if len(self.array) != 3:
				frame = self.array[len(self.array) - 2]
				self.array = self.array[:len(self.array) - 1]
				frame.tkraise()

	def logout(self):
		self.client.get("http://172.16.115.106:8080/logout/")
		self.usertype = ""
		self.topframe.logout()
		self.show_frame("MainWindow")


def start():
	app = SampleApp()
	#app.geometry('500x500')
	#app.attributes('-fullscreen', True)
	w, h = app.winfo_screenwidth(), app.winfo_screenheight()
	app.geometry("%dx%d+0+0" % (w, h))
	app.title("Software Project")
	# app.config(bd=5)
	app.mainloop()