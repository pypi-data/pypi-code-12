import requests
import json
from bs4 import BeautifulSoup
import urllib
import os
import sys

def cleanMess():
	import os
	os.remove('/home/wolfinsta_first_page_json_raw.txt')
	os.remove('/home/wolfinsta_next_json.txt')

def initPageData(user):
	fetch = 'https://www.instagram.com/'+str(user)
	data = requests.get(fetch)
	html = data.text
	soup = BeautifulSoup(html, "lxml")
	script = soup.findAll('script')[6]
	readable = script.string
	cleaned = readable.replace('window._sharedData = ','')
	cleaned = cleaned.strip(';')
	jsonfile = '/home/wolfinsta_first_page_json_raw.txt'
	f = open(jsonfile,'w')
	f.write(cleaned) # python will convert \n to os.linesep
	f.close()
	return jsonfile

def build_dir(username, userid,downloadLocation):
	dirpath = downloadLocation+"/"+username+"_"+str(userid)
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)
		return dirpath
	else:
		return dirpath

def build_imgDir(userdir, image_id):
	return str(userdir)+"/"+str(image_id)+"_.jpg"

def storeJson(filename, json):
	f = open(filename+".txt",'w')
	f.write(str(json)) # python will convert \n to os.linesep
	f.close()
	return filename

def cleanUpNext(userid, startItem):
	cleared = {}
	count = 0
	data = getNextPosts(userid, startItem)
	with open(data) as data_file:
		nextData = json.load(data_file)

	hasNext = nextData['media']['page_info']['has_next_page']
	startsAt = nextData['media']['page_info']['start_cursor']
	endsAt = nextData['media']['page_info']['end_cursor']
	posts = nextData['media']['nodes']
	totalPosts = nextData['media']['count']
	Pages = totalPosts / 30
	print "Found "+ str(totalPosts) + " posts"
	print "Dividing into " + str(Pages) + " pages"
	print "All posts of user need to be buffered first ..Start of download can take some time.."
	cleared[0] = posts

	for x in xrange(Pages):
		newData = getNextPosts(userid, endsAt)
		with open(newData) as newFile:
			newNext = json.load(newFile)

		hasNext = newNext['media']['page_info']['has_next_page']
		startsAt = newNext['media']['page_info']['start_cursor']
		endsAt = newNext['media']['page_info']['end_cursor']
		posts = newNext['media']['nodes']
		cleared[x] = posts

	return cleared


def cleanData(initJsonFile,downloadLocation):
	import os
	theFile = initJsonFile
	with open(initJsonFile) as data_file:
		data = json.load(data_file)

	ProfilePage = data['entry_data']['ProfilePage']
	user = ProfilePage[0]['user']
	cleaned = {}

	userId = user['id']
	firstItem = user['media']['page_info']['start_cursor']
	lastItem = user['media']['page_info']['end_cursor']
	nextPage = user['media']['page_info']['has_next_page']

	theUser = user['username']
	cleaned['username'] = user['username']
	cleaned['following'] = user['follows']['count']
	cleaned['followers'] = user['followed_by']['count']
	cleaned['avatar'] = user['profile_pic_url']
	cleaned['userid'] = userId
	cleaned['description'] = user['biography']
	cleaned['name'] = user['full_name']
	cleaned['posts'] = user['media']['count']

	cleaned['firstItem'] = firstItem
	cleaned['lastItem'] = lastItem
	cleaned['nextPage'] = nextPage

	posts = user['media']['nodes']

	if nextPage == True:
		nextData = cleanUpNext(userId,lastItem)
		for curItem in nextData:
			posts = posts + nextData[curItem]
	cleaned['user_content'] = {}
	
	user_dir = build_dir(user['username'], user['id'],downloadLocation)


	count = 1
	total = len(posts)
	for item in posts:
		if 'caption' in item:
			caption = item['caption']
		else:
			caption = "Default caption now"
		cleaned['user_content'][count] = {}
		cleaned['user_content'][count]['code'] = item['code']
		cleaned['user_content'][count]['published'] = item['date']
		cleaned['user_content'][count]['comments'] = item['comments']['count']
		cleaned['user_content'][count]['likes'] = item['likes']['count']
		cleaned['user_content'][count]['owner'] = item['owner']['id']
		cleaned['user_content'][count]['description'] = caption
		cleaned['user_content'][count]['thumb'] = item['thumbnail_src']
		cleaned['user_content'][count]['image'] = item['display_src']
		cleaned['user_content'][count]['is_video'] = item['is_video']
		cleaned['user_content'][count]['itemid'] = item['id']

		curItemData = cleaned['user_content'][count]
		image_id = item['id']
		urllib.urlretrieve(item['display_src'], build_imgDir(user_dir, image_id))
		#print "Downloading image numbe " + str(count) + "/" + str(total) + " for use "
		print "Downloading image number " + str(count) + "/" + str(total) + " for user: " + theUser
		#print "Storing json for " + str(count)
		#storeJson(user_dir+"/"+str(image_id)+"_json",curItemData)

		if count == total:
			cleanMess()
			print "Completed! All files saved to " + user_dir
			#shutil.make_archive(user_dir+".zip", 'zip', user_dir)

			break
		#print count
		count = count + 1

	#print json.dumps(cleaned)

def getNextPosts(userid, firstItem):
	headers = {
	    'cookie': 'mid=VqseEAAEAAGxfi439_-Fho_gkaOo; s_network=; sessionid=IGSCbcab7e88946f94dd916350a2d731e256c6d0518b83e66e4e1925a907e53fd291%3AzhrsGBH4IovKJdbPoKAtnUniwwHt2Dkh%3A%7B%22asns%22%3A%7B%22202.166.173.132%22%3A55501%2C%22time%22%3A1459151227%7D%7D; ig_pr=1; ig_vw=1366; csrftoken=cc56543904a1ac770c60145febc024e6',
	    'origin': 'https://www.instagram.com',
	    'accept-encoding': 'gzip, deflate',
	    'accept-language': 'en-US,en;q=0.8',
	    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
	    'x-requested-with': 'XMLHttpRequest',
	    'x-csrftoken': 'cc56543904a1ac770c60145febc024e6',
	    'x-instagram-ajax': '1',
	    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
	    'accept': 'application/json, text/javascript, */*; q=0.01',
	    'referer': 'https://www.instagram.com/therock/',
	    'authority': 'www.instagram.com',
	}

	data = 'q=ig_user('+userid+')+%7B+media.after('+firstItem+'%2C+200)+%7B%0A++count%2C%0A++nodes+%7B%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=users%3A%3Ashow'

	requ = requests.post('https://www.instagram.com/query/', headers=headers, data=data)
	newFile = '/home/wolfinsta_next_json.txt'
	f = open(newFile,'w')
	f.write(requ.text) # python will convert \n to os.linesep
	f.close()
	return newFile