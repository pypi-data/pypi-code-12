from Tkinter import *
import json
from encrypt_pass import create_enc_password
import requests
TITLE_FONT = ("Times New Roman", 50, "bold")
Text_FONT  = ("Times New Roman", 15, "italic")


class Login(Frame):
	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		# self.config(bd=5)
		self.controller = controller
		self.grid_columnconfigure(0, weight = 3)
		self.grid_columnconfigure(1, weight = 1)
		self.grid_columnconfigure(2, weight = 1)
		self.grid_columnconfigure(3, weight = 3)
		self.grid_rowconfigure(0, weight = 7)
		self.grid_rowconfigure(1, weight = 1)
		self.grid_rowconfigure(2, weight = 1)
		self.grid_rowconfigure(3, weight = 1)
		self.grid_rowconfigure(4, weight = 1)
		self.grid_rowconfigure(5, weight = 1)
		self.grid_rowconfigure(6, weight = 1)
		self.grid_rowconfigure(7, weight = 1)
		self.grid_rowconfigure(8, weight = 1)
		self.grid_rowconfigure(9, weight = 1)
		self.grid_rowconfigure(10, weight = 7)
		label = Label(self, text="Login", font=TITLE_FONT)
		label.grid(row = 0, column = 1, columnspan = 2, sticky = "nsew")
		# label.pack(side="top", fill="x", pady=10)
		lab0 = Label(self,text="User Name: ", font=Text_FONT)
		lab0.grid(row = 1, column = 1, sticky = "nsew")
		self.ent0 = ent0 = Entry(self,bd=5, font=Text_FONT)
		ent0.grid(row = 1, column = 2, sticky = "nsew")
		lab1 = Label(self,text="Password:", font=Text_FONT)
		lab1.grid(row = 2, column = 1, sticky = "nsew")
		self.ent1 = ent1 = Entry(self,bd=5, show = "*", font=Text_FONT)
		ent1.grid(row = 2, column = 2, sticky = "nsew")
		self.ent1.bind('<Control-x>', lambda e: 'break') #disable cut
		self.ent1.bind('<Control-c>', lambda e: 'break') #disable copy
		self.ent1.bind('<Control-v>', lambda e: 'break') #disable paste
		self.ent1.bind('<Button-3>', lambda e: 'break') #disable right click
		but0 = Button (self,fg="red",text="Login",height="1", command = lambda: self.login(controller), font=Text_FONT)
		but0.grid(row = 4, column = 1, columnspan = 2, sticky = "nsew")
		self.label = label = Label(self, text = "")
		label.grid(row = 5, column = 1, columnspan = 2, sticky = "nsew")

	def login(self, controller):
		username = self.ent0.get()
		password = self.ent1.get()
		if username == "":
			message = "Please enter your username"
		elif password == "":
			message = "Please enter your password"
		else:
			password = create_enc_password(password)
			# print password
			url = 'http://172.16.115.106:8080/login/'
			(controller.client).get(url, proxies = {})
			csrf = dict((controller.client).cookies)['csrftoken']
			# print(csrf)
			message = "Success"
			response = json.loads((controller.client).post(url, data={'username': username, 'password': password, 'csrfmiddlewaretoken': csrf}, proxies={}, headers=dict(Referer=url)).content)
			# print(response.content)
		if message != "Success":
			self.label.config(text=message)
		elif "message" not in response or response["message"] != "Success":
			self.label.config(text=response["message"])
		else:
			controller.usertype = response["usertype"]
			controller.topframe.login()
			controller.show_frame("Coursepage")
		# resp = (controller.client).get('http://172.16.115.106:8080/courselist/')
		# controller.show_frame("Coursepage")
		# print resp.content
		# print(client.headers)