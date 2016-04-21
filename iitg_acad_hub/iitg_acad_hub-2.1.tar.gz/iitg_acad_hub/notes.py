import requests
import os
import time

def uploadFile(file, roll, course):
	url = 'http://172.16.115.76/upload.php'
	files = {'fileToUpload': open(file, 'rb')}
	data = {'roll':roll, 'course':course}
	r = requests.post(url, files=files, data=data)
	return r.status_code	

def listUploads(course):
	url = 'http://172.16.115.76/listfiles.php'
	data = {'course':course}
	r = requests.post(url, data=data)
	# print r.text
	files = r.text.split("\n")[:-1]

	icondir = 'icons/'
	try:
		fileicons = os.listdir(icondir)
	except:
		icondir = 'iitg_acad_hub/icons/'
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
	url = 'http://172.16.115.76/rating.php'
	# print ratingold
	rato = float(ratingold[0:4])
	ratero = int(ratingold[5:-1])
	ratn = str("{0:.2f}".format((rato*ratero+ratingnew)/(ratero+1)))[0:4]
	rating = "_"+ratingold[0:4]+"_"+ratingold[5:-1]
	ratnew = "_"+ratn+"_"+str(ratero+1)


	data = {'course':course, 'file':filename, 'roll':roll,'ratingnew':ratnew,'rating':rating }
	r = requests.post(url, data=data)
	return r.status_code


def downloadFile(filename, filepath, course, roll,rating):
	url = 'http://172.16.115.76/download.php'
	rate = "_"+rating[0:4]+"_"+rating[5:-1]
	data = {'course':course, 'file':filename, 'roll':roll,'rating':rate}
	r = requests.post(url, data=data)

	with open(filepath+'/'+filename, 'wb') as f:
		f.write(r.content)

	# print r.headers
	return r.status_code