from Tkinter import *

def data():
	# label = Label(frame,text = "Question 1")
	# label.pack()
	# text = Text(frame)
	# text.pack()
	# label = Label(frame,text = "Question 1")
	# label.pack()
	# text = Text(frame)
	# text.pack()	
	# label = Label(frame,text = "Question 1")
	# label.pack()
	# text = Text(frame)
	# text.pack()	
	label = Label(frame,text = "Question 1")
	label.pack()
	text = Text(frame)
	text.pack()
	frame.q = 1
	frame.ques = []
	frame.ques.append(text)
	but0 = Button(frame, text = "Add", command = lambda: frame.addquestion())
	but0.pack()

	def addquestion(frame):
		frame.q = frame.q + 1
		for child in frame.winfo_children():
			child.destroy()
		frame.ques = []
		for i in range(frame.q):
			label = Label(frame, text = "Question " + str(i + 1))
			label.pack()
			text = Text(frame)
			text.pack()
			frame.ques.append(text)
		but0 = Button(frame, text = "Add", command = lambda: frame.addquestion())
		but0.pack()
		
def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=600,height=600)

root=Tk()

myframe=Frame(root,relief=GROOVE,width=600,height=600,bd=1)
myframe.place(x=10,y=10)

canvas=Canvas(myframe, width = 600, height = 600)
frame=Frame(canvas)
myscrollbar=Scrollbar(myframe,orient="vertical",command=canvas.yview)
canvas.configure(yscrollcommand=myscrollbar.set)

myscrollbar.pack(side="right",fill="y")
canvas.pack(side="left")
canvas.create_window((0,0),window=frame,anchor='nw')
frame.bind("<Configure>",myfunction)
data()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))
root.mainloop()