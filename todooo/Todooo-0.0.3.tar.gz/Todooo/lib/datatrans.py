#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle
import os
class Sav(object):
	def __init__(self,todo):
		self.data=todo.todolist
		'''self.cursor=todo.cursor
		self.counter=todo.counter
		self.i=todo.i
		self.tmp=todo.tmp'''
		self.list=[todo.cursor,todo.counter,todo.i,todo.tmp]
	def savedata(self,id,title):
		data_path=os.path.join(os.path.dirname(__file__), '../data/usr/%s/%s.dat"%(id,title)') 
		dat1=open(data_path,'wb')

		pickle.dump(self.data,dat1)
		dat1.close()
	def saveargs(self,id,title):
		args_path=os.path.join(os.path.dirname(__file__), '../data/usr/%s/%s_args.dat"%(id,title)')
		dat2=open(args_path,'wb')
		pickle.dump(self.list,dat2)
		dat2.close()
def savefile(todo,userid,title):
	wrote=Sav(todo)
	wrote.savedata(userid,title)
	wrote.saveargs(userid,title)

def loadfile(id,title):
	data_path= os.path.join(os.path.dirname(__file__), '../data/usr/%s/%s.dat"%(id,title)') 
	datafile=open(data_path,'rb')
	listdata=pickle.load(datafile)	
	datafile.close()
	return listdata
def loadargs(id,title):
	args_path=os.path.join(os.path.dirname(__file__), '../data/usr/%s/%s_args.dat"%(id,title)')
	dat3=open(args_path,'rb')
	datalist=pickle.load(dat3)

	return datalist[0][0],datalist[1][0],datalist[2][0],datalist[3][0]

def loadall(userid,today,future,post,comp):
	today.todolist=loadfile(userid,'today')
	future.todolist=loadfile(userid,'future')
	post.todolist=loadfile(userid,'postpone')
	comp.todolist=loadfile(userid,'complete')
	today.cursor[0],today.counter[0],today.i[0],today.tmp[0]=loadargs(userid,'today')
	future.cursor[0],future.counter[0],future.i[0],future.tmp[0]=loadargs(userid,'future')
	post.cursor[0],post.counter[0],post.i[0],post.tmp[0]=loadargs(userid,'postpone')
	comp.cursor[0],comp.counter[0],comp.i[0],comp.tmp[0]=loadargs(userid,'complete')


def saveuser(usrdict,userid):
	user_path=os.path.join(os.path.dirname(__file__), '../data/Userdata.dat')
	f=open(user_path,"w")
	#for line in usrdict.item():
	for k, v in usrdict.items():
		f.writelines('{} {} {} {}'.format(k,v,userid[k],'\n') )
	f.close()

def loaduser():
	user_path=os.path.join(os.path.dirname(__file__), '../data/Userdata.dat')
	g=open(user_path,'r')
	list1=[]
	list2=[]
	list3=[]
	for each in g:
		each=each.strip('\n')
		c=each.split(' ')
		list1.append(c[0])
		list2.append(c[1])
		list3.append(c[2])
	dic=dict(zip(list1,list2))
	dic2=dict(zip(list1,list3))
	return dic,dic2
	g.close()

