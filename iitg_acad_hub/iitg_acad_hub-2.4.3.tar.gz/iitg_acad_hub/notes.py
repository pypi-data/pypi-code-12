"""@package docstring
Documentation for this module.

This module has functions to upload, list and download files. 
"""

import requests
import os
import time
import project


def uploadFile(file, roll, course):
	"""Function to upload a given file to the server.
	Input is file location, roll number and course.
	"""
	url = 'http://172.16.115.76/upload.php'
	files = {'fileToUpload': open(file, 'rb')}
	data = {'roll':roll, 'course':course}
	r = requests.post(url, files=files, data=data)
	return r.status_code	

def listUploads(course):
	"""Function to list all the uploaded notes for a given inpur course
	"""
	url = 'http://172.16.115.76/listfiles.php'
	data = {'course':course}
	r = requests.post(url, data=data)
	# print r.text
	files = r.text.split("\n")[:-1]
	icondir = os.path.dirname(os.path.abspath(project.__file__))+'/icons/'
	fileicons = os.listdir(icondir)
	uploadedby = []
	filename = []
	icons = []
	uploadTime = []
	rating = []

	for i in range(0,len(files),2):
		uploadedby.append(files[i][:9])
		filename.append("".join(files[i].split("_")[0:-2])[9:])
		realTime = time.asctime(time.localtime(int(files[i+1])))
		uploadTime.append(str(realTime))

		try:
			rating.append(files[i].split("_")[-2]+"("+files[i].split("_")[-1]+")")
		except:
			rating.append("")
		flag = 0
		for icon in fileicons:
			if filename[i/2].split('.')[-1] in icon.split('.')[0]:
				flag = 1
				icons.append(icondir+icon)
				break
		if flag is 0:
			icons.append(icondir+'default.png')
	return icons, filename, uploadedby, uploadTime , rating 


def rateFile(filename, course, roll,ratingold, ratingnew):
	"""Function to rate a given file. 
	Updates the rating of the given file by taking inputs as the filename, course, roll number(of the uploader), 
	old rating and the selected rating by the user.
	"""
	url = 'http://172.16.115.76/rating.php'
	print ratingold
	rato = float(ratingold[0:4])
	ratero = int(ratingold[5:-1])
	ratn = str("{0:.2f}".format((rato*ratero+ratingnew)/(ratero+1)))[0:4]
	rating = "_"+ratingold[0:4]+"_"+ratingold[5:-1]
	ratnew = "_"+ratn+"_"+str(ratero+1)


	data = {'course':course, 'file':filename, 'roll':roll,'ratingnew':ratnew,'rating':rating }
	r = requests.post(url, data=data)
	return r.status_code


def downloadFile(filename, filepath, course, roll,rating):
	"""Function to download a given file from the server.
	Input is filename, location(where to be downloaded), course, roll number and rating of the file.
	"""
	url = 'http://172.16.115.76/download.php'
	rate = "_"+rating[0:4]+"_"+rating[5:-1]
	data = {'course':course, 'file':filename, 'roll':roll,'rating':rate}
	r = requests.post(url, data=data)

	with open(filepath+'/'+filename, 'wb') as f:
		f.write(r.content)

	return r.status_code	


