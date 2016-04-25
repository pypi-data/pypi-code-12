from Tkinter import *
import json
import ScrolledText
import os
import tkMessageBox
import getpass
from functools import partial
head_font = ("Helvetica", 22, "bold")
text_font = ("Times New Roman", 18)

class assignment(Frame):
	def __init__(self, parent, controller):								#assignment window 
		Frame.__init__(self, parent)
		self.controller = controller

	def add(self):
		assignment = self.enter.get()
		url = "http://172.16.115.106:8080/addassignment/"
		# print self.controller.course
		response = json.loads((self.controller.controller.client).get(url, params={'assignment': assignment, 'coursename': self.controller.course}, proxies={}).content)
		self.load()

	def load(self):
		response = json.loads(self.controller.controller.client.get("http://172.16.115.106:8080/assignments/", params = {'coursename': self.controller.course}, proxies={}).content)
		for child in self.winfo_children():
			child.destroy()
		framep = Frame(self)
		framep.grid(row=0,column=0,sticky="nsew")
		framep.grid_columnconfigure(0,weight=8)
		framep.grid_columnconfigure(1,weight=2)
		x=0
		for assign in response:
			but = Button(self, text=assign,height=3,width=25, command = partial(self.controller.show_frame, "question", assign))
			but.grid(row=x,column=0,padx=3)
			x=x+1
		self.enter = Entry(self, bd=5)
		self.enter.grid(row=2,column=1,sticky="nsew")
		reg = Button(self,height=1, text = "Add Course", command = lambda: self.add())
		reg.grid(row=3,column=1,sticky="nsew")

class student(Frame):
	def __init__(self, parent, controller):								#student window 
		Frame.__init__(self, parent)
		self.controller = controller

	def load(self):
		for child in self.winfo_children():
			child.destroy()
		client = self.controller.controller.client
		url = "http://172.16.115.106:8080/coursestudentlist/"
		response = json.loads(client.get(url, params = {'coursename': self.controller.course}).content)
		# print response
		self.grid_columnconfigure(0,weight=4)
		self.grid_columnconfigure(1,weight=1)
		self.grid_columnconfigure(2,weight=4)
		x=0
		for key in response:
			stud = response[key]
			but = Button(self, fg = "black", text =  stud["roll_no"] + ":" + stud["name"], height = 2,width=30, command = partial(self.controller.show_frame, "stud_pro", key))
			but.grid(row=x,column=1,sticky="nsew",pady=2)
			x=x+1

class marks(Frame):
	def __init__(self, parent, controller):								#marks window 
		Frame.__init__(self, parent)
		self.controller = controller

	def load(self):
		for child in self.winfo_children():
			child.destroy()
		client = self.controller.controller.client
		url = "http://172.16.115.106:8080/coursestudentlist/"
		response = json.loads(client.get(url, params = {'coursename': self.controller.course}).content)
		# print response
		# self.grid_columnconfigure(0,weight=)
		self.grid_columnconfigure(0,weight =4)
		self.grid_columnconfigure(1,weight =1)
		self.grid_columnconfigure(2,weight =1)
		self.grid_columnconfigure(3,weight =1)
		self.grid_columnconfigure(4,weight =4)
		l0 = Label(self, text = "Roll Number",font=head_font)
		l1 = Label(self, text = "Name",font=head_font)
		l2 = Label(self, text = "Marks",font=head_font)
		l0.grid(row=0,column=1,sticky="nsew")#pack(side = LEFT,padx=4)
		l1.grid(row=0,column=2,sticky="nsew")#pack(side = LEFT,padx=4)
		l2.grid(row=0,column=3,sticky="nsew")#pack(side = LEFT,padx=4)		
		x=1
		for key in response:
			stud = response[key]
			l0 = Label(self, text = stud["roll_no"],font=text_font)
			l1 = Label(self, text = stud["name"],font=text_font)
			l2 = Label(self, text = stud["marks"],font=text_font)
			l0.grid(row=x,column=1,sticky="nsew")#pack(side = LEFT,padx=4)
			l1.grid(row=x,column=2,sticky="nsew")#pack(side = LEFT,padx=4)
			l2.grid(row=x,column=3,sticky="nsew")#pack(side = LEFT,padx=4)
			x= x+1

class question(Frame):
	def __init__(self, parent, controller):								#marks window 
		Frame.__init__(self, parent)
		self.controller = controller
		self.grid_columnconfigure(0, weight = 15000)
		self.grid_columnconfigure(1, weight = 100)
		self.grid_rowconfigure(0, weight=1)
		self.canvas = canvas = Canvas(self,width = 1500,height=1500)
		self.frame = frame = Frame(canvas)
		self.myscrollbar=myscrollbar=Scrollbar(self,orient="vertical",command=canvas.yview)
		canvas.configure(yscrollcommand=myscrollbar.set)
		myscrollbar.pack(side=RIGHT,fill="y")
		canvas.pack(side=TOP)
		canvas.create_window((0,0),window=frame,anchor='nw')
		frame.bind("<Configure>", self.myfunction)
		label = Label(frame,text = "Question 1")
		label.pack(side = LEFT)
		text = Text(frame)
		text.pack()
		text.insert(INSERT, "")
		self.q = 1
		self.ques = []
		self.ques.append(text)
		self.but0 = but0 = Button(frame, text = "Add", command = lambda: self.addquestion())
		but0.pack()
		self.but1 = but1 = Button(frame, text = "Save Assignment", command = lambda: self.save())
		but1.pack()

	def save(self):
		questions = []
		files = {}
		for i in range(self.q):
			questions.append(json.dumps({"question": self.ques[i].get("1.0", END)[:-1], "testcases": self.regex[i].get("1.0", END)[:-1], "ind": str(i + 1)}))
			file = "/home/" + getpass.getuser() + "/.project/" + str(i + 1) + ".c"
			data = self.ccode[i].get("1.0", END)[:-1]
			try:
				os.system("rm " + file)
			except:
				pass
			with open(file, 'w') as f:
				f.write(data)
				f.close()
			files[str(i + 1)] = open(file, 'rb')
		url = "http://172.16.115.106:8080/addquestions/"
		client = self.controller.controller.client
		client.get(url)
		csrf = dict(client.cookies)['csrftoken']
		response = json.loads(client.post(url, data = {'questions': questions, 'csrfmiddlewaretoken': csrf, 'assignment': self.assign, 'coursename': self.controller.course}, files = files, proxies={}).content)
		print response

	def myfunction(self, event):
		# print event
		# print dir(event)
		self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=600,height=600)

	def addquestion(self):
		self.q = self.q + 1
		self.but0.destroy()
		self.but1.destroy()
		label = Label(self.frame, text = "Question " + str(self.q))
		label.pack()
		text = Text(self.frame)
		text.pack()
		text.insert(INSERT, "")
		self.ques.append(text)
		text = Text(self.frame)
		text.pack()
		text.insert(INSERT, "")
		self.regex.append(text)
		writepad = ScrolledText.ScrolledText(self.frame,height=30)
		writepad.insert(INSERT, "")
		writepad.pack(side=TOP)
		self.ccode.append(writepad)
		self.but0 = but0 = Button(self.frame, text = "Add", command = lambda: self.addquestion())
		but0.pack()
		self.but1 = but1 = Button(self.frame, text = "Save Assignment", command = lambda: self.save())
		but1.pack()

	def load(self, assign):
		self.assign = assign
		# print assign
		response = json.loads((((self.controller.controller)).client).get("http://172.16.115.106:8080/assignments/", params = {'coursename': self.controller.course}, proxies={}).content)
		i = 0
		for child in self.frame.winfo_children():
			child.destroy()
		self.canvas.configure(yscrollcommand=self.myscrollbar.set)
		self.canvas.create_window((0,0),window=self.frame,anchor='nw')
		self.frame.bind("<Configure>", self.myfunction)
		self.ques = []
		self.regex = []
		self.ccode = []
		# print response
		# print assign
		# print response
		# print response[assign]
		for _ques in response[assign]:
			i = i + 1
			label = Label(self.frame, text = "Question " + str(i))
			label.pack()
			text = Text(self.frame)
			text.pack()
			text.insert(INSERT, _ques["question"])
			self.ques.append(text)
			text = Text(self.frame)
			text.pack()
			text.insert(INSERT, _ques["testcases"])
			self.regex.append(text)
			writepad = ScrolledText.ScrolledText(self.frame,height=30)
			writepad.insert(INSERT, _ques["correctcode"])
			writepad.pack(side=TOP)
			self.ccode.append(writepad)
		self.q = i
		self.but0 = but0 = Button(self.frame, text = "Add", command = lambda: self.addquestion())
		but0.pack()
		self.but1 = but1 = Button(self.frame, text = "Save Assignment", command = lambda: self.save())
		but1.pack()