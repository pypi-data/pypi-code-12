from Tkinter import *
TITLE_FONT = ("Times New Roman", 50, "bold")
Text_FONT  = ("Times New Roman", 15, "italic")


class MainWindow(Frame):
	def __init__(self, parent, controller):									#window for home page
		Frame.__init__(self, parent)
		self.controller = controller
		label = Label(self, text="Software", font=TITLE_FONT)
		label.pack(side="top", fill="x", pady=15)
		but0 = Button(self, fg="red",text="Login",justify = CENTER,width = "20", height="3",command=lambda: controller.show_frame("Login"), font=Text_FONT)			
		#loads login window
		but1 = Button(self, fg="red",text="SignUp",justify = CENTER,width = "20", height="3",command=lambda: controller.show_frame("SignUp"), font=Text_FONT)
		#loads signup window
		but2 = Button(self, fg="red",text="Editor", height="3",width = "20",command=lambda: controller.show_frame("CodeEditor"), font=Text_FONT)
		#loads editor window
		but0.pack(side = TOP,padx = 5, pady = 5)
		but1.pack(side = TOP,padx = 5, pady = 5)
		but2.pack(side = TOP, pady = 5)
