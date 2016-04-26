from Tkinter import *
Text_FONT  = ("Times New Roman", 15, "italic")

class TopFrame(Frame):
	def __init__(self, parent, controller):									#window for home page
		Frame.__init__(self, parent)
		self.controller = controller
#		self.geometry('500x500')

		but0 = Button(self, fg="red",text="Back", height="1", command=lambda: controller.back(), font=Text_FONT)
		#loads login window
		but0.pack(side = LEFT, padx = 10, pady = 6)
		#functions to restrict visibility of logout button when user is not logged in
	def login(self):
		self.but1 = Button(self, fg = "red", text = "Log Out", height="1", command=lambda:self.controller.logout(), font=Text_FONT)
		self.but1.pack(side = RIGHT, padx = 10, pady = 6)
	def logout(self):
		self.but1.destroy()