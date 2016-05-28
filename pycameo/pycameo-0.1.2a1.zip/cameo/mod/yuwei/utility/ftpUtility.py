#coding: utf-8
import ftplib
import traceback
import io
import os

class ftpUtility:
	
	session = None

	@staticmethod
	def login(strIP, strUser, strPassword, strPort = "21"):
		ftpUtility.session = ftplib.FTP()
		ftpUtility.session.connect(strIP, strPort)
		try:
			ftpUtility.session.login(strUser, strPassword)
		except:
			traceback.print_exc()

	@staticmethod
	def toDir(strDir):
		if(ftpUtility.session == None):
			print("[ftpHelper.toDir] Please login at first")
			return
		try:
			ftpUtility.toRootDir()
			ftpUtility.session.mkd(strDir)
		except:
			print(strDir + " is already exist")
		ftpUtility.session.cwd(strDir)

	@staticmethod
	def toRootDir():
		strPath = ftpUtility.session.pwd()
		print(strPath)
		ftpUtility.session.sendcmd("CDUP")
		if(strPath == ftpUtility.session.pwd()):
			return
		else:
			ftpUtility.toRootDir()


	@staticmethod
	def upload(strFilePath, strUploadName):
		if(ftpUtility.session == None):
			print("[ftpHelper.upload] Please login at first")
			return
		try:
			file = open(strFilePath,'rb')                  # file to send
			ftpUtility.session.storbinary('STOR '+ strUploadName, file)     # send the file
			file.close() 
		except:
			traceback.print_exc() 

	'''
	功能：將整包資料夾的內容上傳
	參數：
		strLocalFolderRoot：本地端要上傳的資料夾路徑
		strParentFolder：上傳後資料夾所在的資料夾(若是None表示放在Root)
	'''
	@staticmethod
	def uploadFolder(strLocalFolderRoot , strParentPath = None):
		if(ftpUtility.session == None):
			print("[ftpHelper.uploadFolder] Please login at first")
			return
		try:
			strRootFolder = os.path.split(strLocalFolderRoot)[1]
			print(strRootFolder)
			for dirname, dirnames, filenames in os.walk(strLocalFolderRoot):
				for filename in filenames:
					strFilePath = os.path.join(dirname, filename)
					strFolderPath, strFileName = os.path.split(strFilePath)
					strRelatePath = os.path.join(strRootFolder, os.path.relpath(dirname, strLocalFolderRoot))
					if(strParentPath != None):
						strRelatePath = os.path.join(strParentPath, strRelatePath)
					ftpUtility.toDir(strRelatePath)
					ftpUtility.upload(strFilePath, strFileName)
					#print("===========================")
					#print(strFolderPath)
					#print(strRelatePath)
					#print(strFileName)

		except:
			traceback.print_exc()

	@staticmethod
	def logout():
		if(ftpUtility.session != None):
			ftpUtility.session.quit()

if __name__ == '__main__':
	ftpUtility.login("210.65.11.231", "cameo", "cameo")
	ftpUtility.uploadFolder("/Users/yuwei/Desktop/TestUpload", "Test")
	#ftpUtility.toDir("testUpload/Test1/Test2/Test3")
	#ftpUtility.upload('/Users/yuwei/Desktop/12512312_1545479272436297_6372105641884188812_n.jpg', "testupload.jpg")
	ftpUtility.logout()