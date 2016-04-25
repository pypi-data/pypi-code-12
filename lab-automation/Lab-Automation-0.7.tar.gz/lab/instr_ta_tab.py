from Tkinter import *
import json
import ScrolledText
import tkMessageBox
import getpass
import subprocess
from functools import partial
from test_case_generation import *
TITLE_FONT = ("Helvetica", 18, "bold")

class stud_pro(Frame):							#displays student profiles for the instructor and tutor
	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

	def load(self, ids):						#loads the frame with assignment names and marks of students
		for child in self.winfo_children():
			child.destroy()
		client = self.controller.controller.client
		url = "http://172.16.115.106:8080/stupro/"
		client.get(url)
		csrf = dict(client.cookies)['csrftoken']
		#decodes response from server containing marks
		response = json.loads(client.post(url, data = {'coursename': self.controller.course, 'sid': ids, 'csrfmiddlewaretoken': csrf}).content)
		q = Frame(self)
		l1 = Label(q, text = "Name: " + response["name"])
		l2 = Label(q, text = "Roll No.: " + response["roll"])
		l3 = Label(q, text = "Total marks: " + str(response["tmarks"]))
		l1.pack(side=LEFT,padx=3)
		l2.pack(side=LEFT,padx=3)
		l3.pack(side=LEFT,padx=3)
		q.pack(side=TOP)
		q1 = Frame(self)
		for key in response["marks"]:	#prints assignment reachable buttons along with marks in that assignment
			q2 = Frame(q1)
			but = Button(q2, text = key, height = 1,width=10, command = partial(self.controller.show_frame, "ansassign", key, ids))
			marks = Label(q2, text = "Marks: " + str(response["marks"][key]))
			but.pack(side = LEFT,padx=3,pady=2)
			marks.pack(side = LEFT,padx=3,pady=2)
			q2.pack(side = TOP)
		q1.pack()

class ansassign(Frame):										#loads frame for students to solve assignment
	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller

	def switch(self, ind):									#switching between questions tabs
		self.frame[ind - 1].tkraise()

	def save(self, ind, qid):								#updates the marks of the solutions of the student
		marks = self.marks[ind - 1].get()
		client = self.controller.controller.client
		url = "http://172.16.115.106:8080/updcodemarks/"
		client.get(url)
		csrf = dict(client.cookies)['csrftoken']
		response = json.loads(client.post(url, data = {'csrfmiddlewaretoken': csrf, 'marks': marks, 'sid': self.sid, 'qid': qid, 'coursename': self.controller.course}, proxies = {}).content)
		print response

	def compile(self, ind):									#compile function for compiling the codes
		code = self.ques[ind - 1].get("1.0", END)[:-1]
		testcase = self.testcase[ind - 1].get("1.0", END)[:-1]
		assignment = "compiling"
		file_code = "/home/" + getpass.getuser() + "/.project/" + self.controller.course + "_" + assignment + "_" + str(ind) + ".c"
		with open(file_code, 'w') as f:
			f.write(code)
			f.close()
		inp_file = "/home/" + getpass.getuser() + "/.project/" + self.controller.course + "_" + assignment + "_" + str(ind) + ".in"
		with open(inp_file, 'w') as f:
			f.write(testcase)
			f.close()
		self.output[ind - 1].delete("1.0", END)
		try:
			subprocess.check_output("gcc " + file_code + " -o " + file_code[:-2], shell = True, stderr = subprocess.STDOUT)
			response = subprocess.check_output(file_code[:-2] + " < " + inp_file, shell = True)
		except Exception as e:
			response = e.output
			response = response[1 + len(file_code):]
		self.output[ind - 1].insert(INSERT, response)

	def test_all(self, ind):								#auto generated multiple test cases for the instructor to check solutions
		code = self.ques[ind - 1].get("1.0", END)[:-1]
		correctcode = self.quest[ind - 1]["correctcode"]
		assignment = "submitedcode"
		file_code_subitted = "/home/" + getpass.getuser() + "/.project/" + self.controller.course + "_" + assignment + "_" + str(ind) + ".c"
		with open(file_code_subitted, 'w') as f:
			f.write(code)
			f.close()
		assignment = "correctcode"
		file_code_correct = "/home/" + getpass.getuser() + "/.project/" + self.controller.course + "_" + assignment + "_" + str(ind) + ".c"
		with open(file_code_correct, 'w') as f:
			f.write(correctcode)
			f.close()
		inp_file = "/home/" + getpass.getuser() + "/.project/" + self.controller.course + "_" + assignment + "_" + str(ind) + ".in"
		output = ""
		flag = 0
		for i in range(10):
			testcase = generate(self.quest[ind - 1]["testcases"])
			with open(inp_file, 'w') as f:
				tc=""
				for line in testcase:
					tc = tc + line + "\n"
				f.write(tc)
				f.close()
			try:
				subprocess.check_output("gcc " + file_code_subitted + " -o " + file_code_subitted[:-2], shell = True, stderr = subprocess.STDOUT)
				response_s = subprocess.check_output(file_code_subitted[:-2] + " < " + inp_file, shell = True)
				subprocess.check_output("gcc " + file_code_correct + " -o " + file_code_correct[:-2], shell = True, stderr = subprocess.STDOUT)
				response_c = subprocess.check_output(file_code_correct[:-2] + " < " + inp_file, shell = True)
				if (response_c != response_s):
					output = "error in case\n"+tc
					flag = 1
					break
			except Exception as e:
				output = "compilation error"
				flag = 1
		if flag == 0:
			output = "Code passed all cases"
		self.output[ind - 1].delete("1.0", END)
		self.output[ind - 1].insert(INSERT, output)


	def gen_cases(self,ind):							#generates single test cases for checking the questions
		self.testcase[ind - 1].delete("1.0",END)
		regex = self.quest[ind - 1]["testcases"]
		testc = generate(regex)
		for line in testc:
			self.testcase[ind - 1].insert(INSERT,line+"\n")

	def load(self, key, ids):							#loads the frame for showingthe solutions submitted by students
		for child in self.winfo_children():
			child.destroy()
		client = self.controller.controller.client
		self.sid = ids
		url = "http://172.16.115.106:8080/ansassign/"
		client.get(url)
		csrf = dict(client.cookies)['csrftoken']
		response = json.loads(client.post(url, data = {'csrfmiddlewaretoken': csrf, 'sid': ids, 'assign': key, 'coursename': self.controller.course}).content)
		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight = 10)
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		frame = Frame(self)
		frame.grid(row = 0, column = 0, sticky = "nsew")
		i = 0
		for ques in response:
			i = i + 1
			but = Button(frame, fg="red",text="Question "+str(i), height="1", command=partial(self.switch, i))
			but.pack(side = LEFT)
		self.frame = []
		self.ques = []
		self.quest = []
		self.marks = []
		self.testcase = []
		self.output = []
		# self.ques.append(text)
		# print response
		# print assign
		# print response
		# print response[assign]
		i = 0
		for _ques in response:
			i = i + 1
			fram1 = Frame(self)
			fram1.grid(row = 1, column = 0, sticky = "nsew")
			fram1.grid_columnconfigure(0,weight =5)
			fram1.grid_columnconfigure(1,weight =5)
			fram1.grid_columnconfigure(2,weight =2)
			fram1.grid_rowconfigure(0,weight =2)
			fram1.grid_rowconfigure(1,weight =5)
			fram1.grid_rowconfigure(2,weight =5)
			fram1.grid_rowconfigure(3,weight =1)
			label = Label(fram1, text = response[_ques]["question"])
			label.grid(row=0,column=0,columnspan=2,sticky="nsew")
			writepad = ScrolledText.ScrolledText(fram1,height=30)
			writepad.insert(INSERT, response[_ques]["file"])
			writepad.grid(row=1,column=0,rowspan=2,sticky="nsew",padx=5,pady=5)
			writepad1 = ScrolledText.ScrolledText(fram1,height=15)
			writepad1.insert(INSERT,"")
			writepad1.grid(row=1,column=1,sticky="nsew",padx=5,pady=5)
			writepad2 = ScrolledText.ScrolledText(fram1,height=15)
			writepad2.insert(INSERT, "")
			writepad2.grid(row=2,column=1,sticky="nsew",padx=5,pady=5)
			ent = Entry(fram1, bd=5)
			ent.grid(row=3,column=0,sticky="nsw")
			ent.insert(INSERT, response[_ques]["marks"])
			self.quest.append(response[_ques])
			self.ques.append(writepad)
			self.testcase.append(writepad1)
			self.output.append(writepad2)
			self.marks.append(ent)
			self.frame.append(fram1)
			but1 = Button(fram1, text = "Update Marks", command = partial(self.save, i, _ques))
			but1.grid(row=3,column=0,sticky="ns")
			but1 = Button(fram1, text = "Compile and Run", command = partial(self.compile, i))
			but1.grid(row=3,column=1,columnspan=2,sticky="nse")
			but1 = Button(fram1, text = "Test All Cases", command = partial(self.test_all, i))
			but1.grid(row=3,column=1,sticky="ns")
			but1 = Button(fram1, text = "Generate Test Case", command = partial(self.gen_cases, i))
			but1.grid(row=3,column=1,sticky="nsw")
		self.frame[0].tkraise()