import time
import os
import hashlib
import sys
import logging
from tqdm import tqdm
from shutil import move
from org_e import utils

py_maj_version = sys.version_info[0]

if py_maj_version < 3:
	from tkFileDialog import askdirectory
elif py_maj_version >= 3:
	from tkinter.filedialog import askdirectory


logging.basicConfig(level=logging.INFO, format='%(message)s')
logging.getLogger('requests').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addFilter(utils.ColorizeFilter())


def recognizeExtension(myList, value):
	for outerI, innerI in enumerate(myList):
		try:
			return (outerI, innerI.index(value))
		except ValueError:
			pass
	return 0

#The first element of each of these lists is the name of the folder
folderNames             = [ 'Previous Folders', 'Audio', 'Compressed Files', 'Codes', 'Database Files', os.path.join('Office Files', 'Documents'), 'Emails', 'Executables', 'Fonts', 'Models', 'Videos', 'Images', 'PDFs and Page Layout Docs', os.path.join('Office Files', 'Presentations'), os.path.join('Office Files', 'Spreadsheets'), 'Text and Data Files', 'Torrents', 'Webpages']
audioExtensions         = [ folderNames[1], '.wav', '.mid', '.midi', '.wma', '.mp3', '.ogg', '.rma', '.m4a', 'm3u', '.aif', '.mid' ]
compressedExtensions    = [ folderNames[2], '.zip', '.rar', '.7z', '.gz', '.iso', '.tar', '.zipx', '.pkg', '.gz', '.deb', '.xz', '.bz2', '.tgz']
codeExtensions          = [ folderNames[3], '.py', '.cpp', '.cs', '.xml', '.java', '.c', '.xaml', '.m', '.pyd', '.pyc', '.class', '.h', '.pl', '.sh', '.sln', '.vb', '.vcxproj', '.xcodeproj' ]
databaseExtensions      = [ folderNames[4], '.accdb', '.db', '.dbf', '.mdb', '.pdb', '.sql']
documentExtensions      = [ folderNames[5], '.doc' ,'.docx', '.odf', '.docm', '.dot', '.dotx', '.pages', '.wpd', '.wps' ]
emailExtensions         = [ folderNames[6], '.msg']
exeExtensions           = [ folderNames[7], '.exe' , '.msi', '.apk', '.app', '.bat', '.cgi', '.com', '.gadget', '.jar', '.wsf', '']  #there's a safeguard for folders annyways
fontExtensions          = [ folderNames[8],  '.fnt', '.fon', '.otf', '.ttf']
modellingExtensions     = [ folderNames[9], '.3dm', '.3ds', '.max', '.obj', '.dwg', '.dxf' ]
videoExtensions         = [ folderNames[10], '.avi', '.mp4', '.divx', '.wmv', '.mkv', '.srt', '.3gp', '.flv', '.m4v', '.mov', '.mpg' ]
picExtensions           = [ folderNames[11], '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.ico', '.dcm', '.thm', '.tga', '.svg', '.tif', '.psd', '.ai', '.pspimage' ]
pdfExtensions           = [ folderNames[12], '.pdf', '.indd', '.tex', '.epub' ]
presentationExtenstions = [ folderNames[13], '.ppt' ,'.pptx', '.pptm', '.pot', '.potx', '.potm', '.phm', '.phmx', '.pps', '.ppsx', '.ppam', '.ppa', '.odp', '.key']
spreadsheetExtensions   = [ folderNames[14], '.xls' ,'.xlsx', '.xlsm', '.xlsx', '.xlsb', '.xltx', '.xltm', '.xls', '.xlt', '.xlsx', '.xlam', '.xla', '.xlw', '.ods', 'xlr' ]
textFileExtensions      = [ folderNames[15], '.txt', '.rtf', '.log', '.rst', '.in', '.md', '.csv', '.dat', '.sdf', '.bak', '.tmp',  ]
torrentExtensions       = [ folderNames[16], '.torrent', '.tor', '.torr' ]
webpageExtensions       = [ folderNames[17], '.js', '.htm', '.html', '.css', '.asp', '.aspx', '.cer', '.csr', '.jsp', '.php', '.rss', '.xhtml', '.crx', ]

validExtensions = [videoExtensions, audioExtensions, picExtensions, pdfExtensions, documentExtensions, presentationExtenstions, spreadsheetExtensions, codeExtensions, exeExtensions, compressedExtensions, torrentExtensions, webpageExtensions, textFileExtensions, emailExtensions, databaseExtensions, modellingExtensions, fontExtensions]




def main():
	logger.info('Org E. Declutter your folders with a single click. Please choose your Directory')
	time.sleep(1)

	original_directory = askdirectory(initialdir='.',title='Please select a directory')
	try:
		logger.info('The chosen directory is ' + original_directory)
	except TypeError:
		logger.error('Please choose a valid directory')
		sys.exit(0)

	new_directory = original_directory

	FileList = os.listdir(original_directory)
	unknownExtensions=[]

	for i in tqdm(range(len(FileList))):
		#print(File)
		File = FileList[i]
		extension = ''.join(os.path.splitext(File)[1])
		name = ''.join(os.path.splitext(File)[0])
		ext = extension.strip('.')
		if(File=='desktop.ini'):
			continue
		if os.path.isdir(os.path.join(original_directory,File)):
			if(File in folderNames):
				pass
			else:
				if(os.path.exists(os.path.join(new_directory, folderNames[0]))) != True:
					os.makedirs(os.path.join(new_directory, folderNames[0]))
				move(os.path.join(original_directory, File), os.path.join(new_directory, folderNames[0], File))
			continue
		elif recognizeExtension(validExtensions, extension.lower()):
			outerIndex, innerIndex = recognizeExtension(validExtensions, extension.lower())
			if os.path.exists(os.path.join(new_directory, validExtensions[outerIndex][0], File)):
				Data = open(os.path.join(original_directory, File), 'r').read()
				m = hashlib.sha1()
				m.update(Data)
				h = (m.hexdigest())[0:5]
				file(os.path.join(new_directory, validExtensions[outerIndex][0], name+'-'+h+extension), 'w').write(Data)
				logger.debug(File, ' ','-->',' ',name+'-'+h+'.'+validExtensions[outerIndex][0])
				os.remove(os.path.join(original_directory, File))

			elif os.path.exists(os.path.join(new_directory, validExtensions[outerIndex][0])):
				move(os.path.join(original_directory, File), os.path.join(new_directory, validExtensions[outerIndex][0], File))
			elif os.path.exists(os.path.join(new_directory, validExtensions[outerIndex][0])) != True:
				os.makedirs(os.path.join(new_directory, validExtensions[outerIndex][0]))
				move(os.path.join(original_directory, File), os.path.join(new_directory, validExtensions[outerIndex][0], File))
			unknownExtensions.append(extension)

	if(len(unknownExtensions)>0):
		logger.debug(extension, ' Extension Unknown. Kindly inform the developer at rsnk96@gmail.com')
	logger.info('%s has successfully been decluttered!' %original_directory)