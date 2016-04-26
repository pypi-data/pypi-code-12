from Tkinter import *
import json
import tkMessageBox
import ScrolledText
import getpass
import subprocess
import tkFileDialog
from functools import partial
text_font = ("Times New Roman", 15)
text1_font = ("Helvetica", 18, "bold")

class assignment(Frame):
	def __init__(self, parent, controller):								#assignment frame-Can see the asssignments and solve them
		Frame.__init__(self, parent)
		self.controller = controller
		self.grid_columnconfigure(0,weight = 10)
		self.grid_columnconfigure(1,weight = 2)
		self.grid_columnconfigure(2,weight = 10)
	def load(self):														#loads the assignment frame
		response = json.loads(self.controller.controller.client.get("http://172.16.115.106:8080/assignments/", params = {'coursename': self.controller.course}, proxies={}).content)
		for child in self.winfo_children():
			child.destroy()
		x=0
		for assign in response:
			but = Button(self, text=assign,height=4,width=50,  command = partial(self.controller.show_frame, "answer", assign))
			but.grid(row=x,column=1,sticky="nsew",padx=300,pady=2)
			x = x + 1

class stud_pro(Frame):
	def __init__(self, parent, controller):								#shows the students profile with his/her marks in different assignments
		Frame.__init__(self, parent)
		self.controller = controller

	def load(self):
		for child in self.winfo_children():
			child.destroy()
		client = self.controller.controller.client
		url = "http://172.16.115.106:8080/stupro/"
		client.get(url)
		csrf = dict(client.cookies)['csrftoken']
		response = json.loads(client.post(url, data = {'coursename': self.controller.course, 'csrfmiddlewaretoken': csrf}).content)
		q = Frame(self)
		q.grid_columnconfigure(0,weight=2)
		q.grid_columnconfigure(1,weight=2)
		q.grid_columnconfigure(2,weight=2)
		l1 = Label(q,font=text1_font, text = "Name: " + response["name"])
		l2 = Label(q,font=text1_font, text = "Roll No.: " + response["roll"])
		l3 = Label(q,font=text1_font, text = "Total marks: " + str(response["tmarks"]))
		l1.grid(row=0,column=0,sticky="nsew",padx=15)
		l2.grid(row=0,column=1,sticky="nsew",padx=15)
		l3.grid(row=0,column=2,sticky="nsew",padx=15)
		q.pack(side=TOP,fill=X)
		q1 = Frame(self)
		q2 = Frame(q1)
		q2.pack()
		q2.grid_columnconfigure(0,weight=2)
		q2.grid_columnconfigure(1,weight=2)
		x=0
		for key in response["marks"]:
			but = Label(q2, text = key, height = 1,font=text_font)
			marks = Label(q2, text = "Marks: " + str(response["marks"][key]),font=text_font)
			but.grid(row=x,column=0,sticky="nsew",padx=6)
			marks.grid(row=x,column=1,sticky="nsew",padx=6)
			x=x+1
		q1.pack()

class answer(Frame):
	def __init__(self, parent, controller):								#Frame for students to answer the questionsfor assignments
		Frame.__init__(self, parent)
		self.controller = controller

	def save(self, i):													#save the assignment
		data = self.ques[i - 1].get("1.0", END)[:-1]
		question = self.quest[i - 1]
		coursename = self.controller.course
		assignment = self.assign
		file = "/home/" + getpass.getuser() + "/.project/" + coursename + "_" + assignment + "_" + str(i) + ".c"
		with open(file, 'w') as f:
			f.write(data)
			f.close()
		url = "http://172.16.115.106:8080/savesubmission/"
		(self.controller.controller.client).get(url)
		csrf = dict((self.controller.controller.client).cookies)['csrftoken']
		response = json.loads((((self.controller.controller)).client).post(url, data = {'coursename': coursename, 'question': question['question'], 'assign': assignment, 'csrfmiddlewaretoken': csrf}, files = {'code': open(file, 'rb')}, proxies={}).content)

	def switch(self, ind):												#switches between different questions of a assignment
		self.frame[ind - 1].tkraise()

	def compile(self, ind):												#for compiling the written code
		code = self.ques[ind - 1].get("1.0", END)[:-1]
		inp = self.inp[ind - 1].get("1.0", END)[:-1]
		assignment = self.assign
		file_code = "/home/" + getpass.getuser() + "/.project/" + self.controller.course + "_" + assignment + "_" + str(ind) + ".c"
		with open(file_code, 'w') as f:
			f.write(code)
			f.close()
		inp_file = "/home/" + getpass.getuser() + "/.project/" + self.controller.course + "_" + assignment + "_" + str(ind) + ".in"
		with open(inp_file, 'w') as f:
			f.write(inp)
			f.close()
		self.output[ind - 1].delete("1.0", END)
		try:
			subprocess.check_output("gcc " + file_code + " -o " + file_code[:-2], shell = True, stderr = subprocess.STDOUT)
			response = subprocess.check_output(file_code[:-2] + " < " + inp_file, shell = True)
		except Exception as e:
			response = e.output
			response = response[1 + len(file_code):]
		self.output[ind - 1].insert(INSERT, response)

	def load(self, assign):											#loads the question solving frame
		self.assign = assign
		response = json.loads((((self.controller.controller)).client).get("http://172.16.115.106:8080/assignments/", params = {'coursename': self.controller.course}, proxies={}).content)
		for child in self.winfo_children():
			child.destroy()
		i = 0
		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight = 10)
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		frame = Frame(self)
		frame.grid(row = 0, column = 0, sticky = "nsew")
		for ques in response[assign]:
			i = i + 1
			but = Button(frame, fg="red",text="Question "+str(i), height="1", command=partial(self.switch, i))
			but.pack(side = LEFT)
		self.frame = []
		self.ques = []
		self.quest = []
		self.inp = []
		self.output = []
		i = 0
		for _ques in response[assign]:
			i = i + 1
			frame1 = Frame(self)
			frame1.grid(row = 1, column = 0, sticky = "nsew")			#writepads for code editing, input and output
			frame1.grid_columnconfigure(0,weight =1)
			frame1.grid_columnconfigure(1,weight =1)
			frame1.grid_rowconfigure(0,weight =2)
			frame1.grid_rowconfigure(1,weight =5)
			frame1.grid_rowconfigure(2,weight =5)
			frame1.grid_rowconfigure(3,weight =1)
			label = Label(frame1, text = _ques["question"])
			label.grid(row=0,column=0,columnspan=2,sticky="nsew")
			writepad = ScrolledText.ScrolledText(frame1,height=30)
			writepad.insert(INSERT, "")
			writepad.grid(row=1,column=0,rowspan=2,sticky="nsew",padx=5,pady=5)
			writepad1 = ScrolledText.ScrolledText(frame1,height=15)
			writepad1.insert(INSERT, "")
			writepad1.grid(row=1,column=1,sticky="nsew",padx=5,pady=5)
			writepad2 = ScrolledText.ScrolledText(frame1,height=15)
			writepad2.insert(INSERT, "")
			writepad2.grid(row=2,column=1,sticky="nsew",padx=5,pady=5)
			self.ques.append(writepad)
			self.quest.append(_ques)
			self.inp.append(writepad1)
			self.output.append(writepad2)
			self.frame.append(frame1)
			but1 = Button(frame1, text = "Save", command = partial(self.save, i))
			but1.grid(row=3,column=0,sticky="nsw")
			but1 = Button(frame1, text = "Compile and Run", command = partial(self.compile, i))
			but1.grid(row=3,column=1,sticky="nse")
		self.frame[0].tkraise()