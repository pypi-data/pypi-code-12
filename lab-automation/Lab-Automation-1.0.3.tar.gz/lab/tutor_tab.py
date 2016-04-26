from Tkinter import *
import json
import tkMessageBox
from functools import partial
head_font = ("Helvetica", 22, "bold")
text_font = ("Times New Roman", 18)

class assignment(Frame):
	def __init__(self, parent, controller):								#assignment window fort utor to see the asssignments
		Frame.__init__(self, parent)
		self.controller = controller
		self.enter = enter = Entry(self, bd=5)
		enter.pack(side=TOP)

	def load(self):														#loads assignments created by Instructors
		response = json.loads(self.controller.controller.client.get("http://172.16.115.106:8080/assignments/", params = {'coursename': self.controller.course}, proxies={}).content)
		for child in self.winfo_children():
			child.destroy()
		for assign in response:
			but = Button(self, text=assign,height=3,width=50, command = partial(self.controller.show_frame, "question", assign))
			but.pack(side=TOP,pady=1)


class student(Frame):
	def __init__(self, parent, controller):								#student window 
		Frame.__init__(self, parent)
		self.controller = controller

	def add_selection(self, roll_no, studd):							#For Tutor to add students under him
		self.students.menu.delete(studd)
		client = self.controller.controller.client
		url = "http://172.16.115.106:8080/addtastud/"
		client.get(url)
		csrf = dict(client.cookies)['csrftoken']
		response = json.loads(client.post(url, data = {'coursename': self.controller.course, 'roll_no': roll_no, 'csrfmiddlewaretoken': csrf}).content)
		self.load()

	def load(self):														#Loads the students frame with the selected students by TA
		for child in self.winfo_children():
			child.destroy()
		client = self.controller.controller.client
		url = "http://172.16.115.106:8080/coursestudentlist/"
		all_list = json.loads(client.get(url, params = {'coursename': self.controller.course}).content)
		url = "http://172.16.115.106:8080/tastudents/"
		client.get(url)
		csrf = dict(client.cookies)['csrftoken']
		ta_students = json.loads(client.post(url, data = {'coursename': self.controller.course, 'csrfmiddlewaretoken': csrf}).content)
		# print response
		self.students = students = Menubutton(self, text = "Select Students",width=15 )
		students.grid()
		students.menu = Menu(students)
		students["menu"] = students.menu
		for stud in all_list:
			if stud not in ta_students:
				students.menu.add_checkbutton(label = all_list[stud]["name"] + ":" + all_list[stud]["roll_no"], variable = all_list[stud]["roll_no"], command = partial(self.add_selection, all_list[stud]["roll_no"], all_list[stud]["name"] + ":" + all_list[stud]["roll_no"]))
		students.pack()

		for key in ta_students:
			stud = ta_students[key]
			but = Button(self, fg = "black", text = stud["name"] + ":" + stud["roll_no"], height = 2,width = 15, command = partial(self.controller.show_frame, "stud_pro", key))
			but.pack(pady=1)

class marks(Frame):
	def __init__(self, parent, controller):								#marks frame -Sows marks of students under Tutor
		Frame.__init__(self, parent)
		self.controller = controller									

	def load(self):														#loads the marks frame with marks and response collected from database
		for child in self.winfo_children():
			child.destroy()
		client = self.controller.controller.client
		url = "http://172.16.115.106:8080/tastudents/"
		client.get(url)
		csrf = dict(client.cookies)['csrftoken']
		response = json.loads(client.post(url, data = {'coursename': self.controller.course, 'csrfmiddlewaretoken': csrf}).content)
		# print response
		self.grid_columnconfigure(0,weight =4)
		self.grid_columnconfigure(1,weight =1)
		self.grid_columnconfigure(2,weight =1)
		self.grid_columnconfigure(3,weight =1)
		self.grid_columnconfigure(4,weight =4)
		l0 = Label(self, text = "Roll Number",font=head_font)
		l1 = Label(self, text = "Name",font=head_font)
		l2 = Label(self, text = "Marks",font=head_font)
		l0.grid(row=0,column=1,sticky="nsew")
		l1.grid(row=0,column=2,sticky="nsew")
		l2.grid(row=0,column=3,sticky="nsew")		
		x=1
		for key in response:
			stud = response[key]
			l0 = Label(self, text = stud["roll_no"],font=text_font)
			l1 = Label(self, text = stud["name"],font=text_font)
			l2 = Label(self, text = stud["marks"],font=text_font)
			l0.grid(row=x,column=1,sticky="nsew")
			l1.grid(row=x,column=2,sticky="nsew")
			l2.grid(row=x,column=3,sticky="nsew")
			x= x+1

class question(Frame):
	def __init__(self, parent, controller):								#question frame for tutor
		Frame.__init__(self, parent)
		self.controller = controller
		self.canvas = canvas = Canvas(self)
		self.frame = frame = Frame(canvas)
		self.myscrollbar=myscrollbar=Scrollbar(self,orient="vertical",command=canvas.yview)
		canvas.configure(yscrollcommand=myscrollbar.set)
		myscrollbar.pack(side="right",fill="y")
		canvas.pack(side="left",fill = X)
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

	def myfunction(self, event):
		# print event
		# print dir(event)
		self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=600,height=600)

	def load(self, assign):											#loads the questions for the respective frames
		self.assign = assign
		# print assign
		response = json.loads((((self.controller.controller)).client).get("http://172.16.115.106:8080/assignments/", params = {'coursename': self.controller.course}, proxies={}).content)
		i = 0
		for child in self.frame.winfo_children():
			child.destroy()
		self.ques = []
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
		self.q = i