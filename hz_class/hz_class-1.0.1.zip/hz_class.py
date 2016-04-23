# coding = utf8

import socket,os,sys
from functools import reduce

# python 不存在 直接定义常量/静态变量的修饰符 const/static

# 基类
class Person(object):
	
	def __init__(self,str):
		print(str)
	
	# 当前实例可提供的相应功能
	def readme(self): 
		print(self.introduction)
		
	# 类/应用场景
	def readwe(self):
		list_name = ["Lee","Ailisi","Kuke","Heike","Accest"]
		list_func = ["算数","封装函数","文件操作","网络","数据转换"]
		dict_we = dict(zip(list_name,list_func))
		
		for item in dict_we.items():
			print("%10s : %10s" % item,end="\r\n")
			
		
# 算数 lee		
class Lee(Person):
	
	introduction = "Hello,接下来由我来提供算数方法"
	
	__goldensection = 1.618
	
	def __init__(self):
		Person.__init__(self,self.introduction)
	

	# 高斯公式 	
	def gaosi(self,startNum,endNum):							
	
		if not isinstance(startNum,int) or not isinstance(endNum,int):
			raise TypeError("arguments type is not int")
		elif startNum > endNum:
			raise ValueError("startNum greater than endNum")
		
		# 开始与结束的差值
		val = (endNum - startNum)								
		
		# 决定单双数 需要走的算法模式
		if val%2 > 0:											
			return int(0.5 * (val + 1)*(startNum + endNum))
		
		return int(0.5 * (val)*(startNum + endNum) + (startNum + endNum)* 0.5)
	

	# 黄金分割对比值 / b:反算	
	def golden(self,*arr,b = False):							
		if b:
			return tuple(map(lambda x:round(x/self.__goldensection,3),arr))
		return tuple(map(lambda x:round(x*self.__goldensection,3),arr))
	
	
	
	# 默认 从0累加 复用存在的值	
	def reduce(self,endNum,startNum=0,fn = lambda x,y : x+y):	
		return reduce(fn,range(startNum,endNum))
	
	
	
	# 确保传入参数/迭代对象都可执行	返回迭代对象 外部决定类型
	def map(self,*arr,fn):										
		try:													
			isinstance(*arr,list)
			return map(fn,*arr)
		except TypeError as err:
			#print(err)
			return map(fn,arr)
	
	def filter(self,*arr,fn):									
		try:
			isinstance(*arr,list)
			return filter(fn,*arr)
		except TypeError:
			return filter(fn,arr)

			
			
			
			
# 预封装函数 ailisi
class Ailisi(Person):

	introduction = "Hello,接下来就由大名鼎鼎的爱丽丝为您提供服务";

	def __init__(self):
		Person.__init__(self,self.introduction)

		

# 文件操作	kuke
class Kuke(Person):

	introduction = "Hello,有关文件操作的就交给我吧!"

	def __init__(self):
		Person.__init__(self,self.introduction)
	
	# 复制文件
	def copy(self,current_word,new_word):
		# 复制之前判定文件是否存在
		# 新的目录下是否存在同名的文件
		pass
		
	# 移动文件
	def mv(self):
		pass
		
	
	
# 网络流 heike
class Heike(Person):

	introduction = "你好,我叫Heike,提供ip/tcp/socket等相关方法"

	__userName = None

	def __init__(self):
		Person.__init__(self,self.introduction)
		
	@property
	def name(self):
		if not self.__userName:
			self.__userName = socket.gethostname()
		return self.__userName
	@name.setter
	def name(self,str = socket.gethostname()):
		self.__userName = str
	
	def ip(self,website):
		return socket.gethostbyname(website)
	

# 序列转换/数据转换 
class Accest(Person):

	introduction = "转换数据什么的,就交给我吧"

	def __init__(self):
		Person.__init__(self,self.introduction)




		
if __name__ == "__main__":
	a = Lee()
	a.readwe()
	
	

