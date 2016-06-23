import os
import sys
from shutil import move

py_maj_version = sys.version_info[0]

if py_maj_version < 3:
	from tkFileDialog import askdirectory
elif py_maj_version >= 3:
	from tkinter.filedialog import askdirectory


folderNames = [ 'Audio', 'Compressed Files', 'Codes', 'Database Files', os.path.join('Office Files', 'Documents'), 'Emails', 'Executables', 'Fonts', 'Models', 'Videos', 'Images', 'PDFs and Page Layout Docs', os.path.join('Office Files', 'Presentations'), os.path.join('Office Files', 'Spreadsheets'), 'Text and Data Files', 'Torrents', 'Webpages']


original_directory = ''+askdirectory(initialdir='.',title='Please select a directory')
try:
	print('The chosen directory is ' + original_directory)
except TypeError:
	print('Please choose a valid directory')
	sys.exit(0)
if(original_directory==''):
	print('Please choose a valid directory')
	sys.exit(0)

new_directory = original_directory

FileList = os.listdir(original_directory)

for parent, children, files in os.walk(original_directory):
	# print('Parent: ', parent,'\tChildren: ', children,'\tFile: ', files,'\n')
	if(len(children) > 0):
		for nowFolder in children:
			if nowFolder in folderNames:
				FileList = os.listdir(os.path.join(parent, nowFolder))
				for nowFile in FileList:
					if ':' in nowFile:
						continue
					move(os.path.join(parent, nowFolder, nowFile), os.path.join(parent, nowFile))
					print('Moving: ',os.path.join(parent, nowFolder, nowFile))