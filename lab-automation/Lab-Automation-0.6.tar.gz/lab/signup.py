from Tkinter import *
import json
import requests
from encrypt_pass import create_enc_password
TITLE_FONT = ("Times New Roman", 50, "bold")
Text_FONT  = ("Times New Roman", 15, "italic")
tab_FONT  = ("Times New Roman", 15, "italic")

class SignUp(Frame):
	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller
		self.grid_columnconfigure(0, weight = 9)
		self.grid_columnconfigure(1, weight = 1)
		self.grid_columnconfigure(2, weight = 1)
		self.grid_columnconfigure(3, weight = 1)
		self.grid_columnconfigure(4, weight = 1)
		self.grid_columnconfigure(5, weight = 1)
		self.grid_columnconfigure(6, weight = 1)
		self.grid_columnconfigure(7, weight = 9)
		self.grid_rowconfigure(0, weight = 10)
		self.grid_rowconfigure(1, weight = 1)
		self.grid_rowconfigure(2, weight = 1)
		self.grid_rowconfigure(3, weight = 1)
		self.grid_rowconfigure(4, weight = 1)
		self.grid_rowconfigure(5, weight = 1)
		self.grid_rowconfigure(6, weight = 1)
		self.grid_rowconfigure(7, weight = 1)
		self.grid_rowconfigure(8, weight = 1)
		self.grid_rowconfigure(9, weight = 1)
		self.grid_rowconfigure(10, weight = 10)
		self.label = label = Label(self, text="Sign Up", font=TITLE_FONT)
		label.grid(row = 0, column = 2,columnspan = 4, sticky = "nsew")
		self.var = StringVar()
		self.var.set("Student")
		self.ent6 = ent6 = Radiobutton(self, text="Student", variable = self.var, value = "Student", command = lambda: self.select(), font=tab_FONT)
		ent6.grid(row = 1, column = 5,columnspan = 2)
		self.ent7 = ent7 = Radiobutton(self, text="Tutor", variable = self.var, value = "Tutor", command = lambda: self.select(), font=tab_FONT)
		ent7.grid(row = 1, column = 3,columnspan = 2)
		self.ent8 = ent8 = Radiobutton(self, text="Instructor", variable = self.var, value = "Instructor", command = lambda: self.select(), font=tab_FONT)
		ent8.grid(row = 1, column = 1, columnspan = 2)
		lab4 = Label(self,text="Name: ", height = 1, font=Text_FONT)
		lab4.grid(row = 2, column = 1, columnspan = 3, sticky = "nsew")
		self.ent4 = ent4 = Entry(self,bd=5, font=Text_FONT)
		ent4.grid(row = 2, column = 4, columnspan = 3, sticky = "nsew")
		lab0 = Label(self,text="User Name: ", font=Text_FONT)
		lab0.grid(row = 3, column = 1, columnspan = 3, sticky = "nsew")
		self.ent0 = ent0 = Entry(self,bd=5, font=Text_FONT)
		ent0.grid(row = 3, column = 4, columnspan = 3, sticky = "nsew")
		self.lab5 = lab5 = Label(self,text="Roll number: ", font=Text_FONT)
		lab5.grid(row = 4, column = 1, columnspan = 3, sticky = "nsew")
		self.ent5 = ent5 = Entry(self,bd=5, font=Text_FONT)
		ent5.grid(row = 4, column = 4, columnspan = 3, sticky = "nsew")
		lab1 = Label(self,text="Webmail Id:", font=Text_FONT)
		lab1.grid(row = 5, column = 1, columnspan = 3, sticky = "nsew")
		self.ent1 = ent1 = Entry(self,bd=5, font=Text_FONT)
		ent1.grid(row = 5, column = 4, columnspan = 3, sticky = "nsew")
		lab9 = self.lab9 = Label(self, text = "Instructor webmail", state = "disabled", font=Text_FONT)
		lab9.grid(row = 6, column = 1, columnspan = 3, sticky = "nsew")
		ent9 = self.ent9 = Entry(self, bd=5, state = "disabled", font=Text_FONT)
		ent9.grid(row = 6, column = 4, columnspan = 3, sticky = "nsew")
		lab2 = Label(self,text="Password: ", font=Text_FONT)
		lab2.grid(row = 7, column = 1, columnspan = 3, sticky = "nsew")
		self.ent2 = ent2 = Entry(self,bd=5, show="*", font=Text_FONT)
		ent2.grid(row = 7, column = 4, columnspan = 3, sticky = "nsew")
		self.ent2.bind('<Control-x>', lambda e: 'break') #disable cut
		self.ent2.bind('<Control-c>', lambda e: 'break') #disable copy
		self.ent2.bind('<Control-v>', lambda e: 'break') #disable paste
		self.ent2.bind('<Button-3>', lambda e: 'break') #disable right click
		lab3 = Label(self,text="Confirm Password:", font=Text_FONT)
		lab3.grid(row = 8, column = 1, columnspan = 3, sticky = "nsew")
		self.ent3 = ent3 = Entry(self,bd=5, show = "*", font=Text_FONT)
		ent3.grid(row = 8, column = 4, columnspan = 3, sticky = "nsew")
		self.ent3.bind('<Control-x>', lambda e: 'break') #Taken from https://www.stackoverflow.com/questions/21934348/disabling-copy-paste-action-from-the-tkinter-entry
		self.ent3.bind('<Control-c>', lambda e: 'break')
		self.ent3.bind('<Control-v>', lambda e: 'break')
		self.ent3.bind('<Button-3>', lambda e: 'break')
		but0 = Button (self,fg="red",text="SignUp",height="1", command = lambda: self.register(controller), font=Text_FONT)
		but0.grid(row = 9, column = 1,columnspan = 6,pady = 4, sticky = "nsew")
		self.label = label = Label(self, text = "", font=Text_FONT)
		label.grid(row = 10, column = 4, sticky = "nsew")

	def register(self, controller):
		username = self.ent0.get()
		password = self.ent2.get()
		cnf_password = self.ent3.get()
		roll_no = self.ent5.get()
		webmail = self.ent1.get()
		name = self.ent4.get()
		user = self.var.get()
		instructr = self.ent9.get()
		if name == "":
			message = "Please enter your name"
		elif username == "":
			message = "Please enter username"
		elif roll_no == "" and user != "Instructor":
			message = "Please enter roll number"
		elif webmail == "":
			message = "Please enter webmail"
		elif password == "":
			message = "Please enter password"
		elif cnf_password == "":
			message = "Please enter confirm password"
		elif instructr == "" and user == "Tutor":
			message = "Please enter your supervisor's webmail"
		elif(password != cnf_password):
			message = "Password didn't matched"
		elif(len(password) <= 8):
			message = "Password should be atleast 9 character long"
		else:
			password = create_enc_password(password)
			url = 'http://172.16.115.106:8080/register/'
			controller.client.get(url)
			csrf = dict(controller.client.cookies)['csrftoken']
			message = "Success"
			response = json.loads(controller.client.post(url, data={'username': username, 'password': password, 'webmail': webmail, 'roll_no': roll_no, 'name': name, 'user': user, 'instructr': instructr, 'csrfmiddlewaretoken': csrf}, proxies={}, headers=dict(Referer=url)).content)
		if message != "Success":
			self.label.config(text=message)
		elif "message" not in response or response["message"] != "Success":
			self.label.config(text=response["message"])
		else:
			controller.usertype = response["usertype"]
			controller.topframe.login()
			controller.show_frame("Coursepage")

	def select(self):
		# print self.var.get()
		if self.var.get() == "Instructor":
			self.lab5.config(state = "disabled")
			self.ent5.config(state = "disabled")
		else:
			self.ent5.config(state = "normal")
			self.lab5.config(state = "normal")

		if self.var.get() == "Tutor":
			self.lab9.config(state = "normal")
			self.ent9.config(state = "normal")
		else:
			self.lab9.config(state = "disabled")
			self.ent9.config(state = "disabled")