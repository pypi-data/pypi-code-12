# ref:
#	http://wescpy.blogspot.com/2014/11/authorized-google-api-access-from-python.html
#	http://wescpy.blogspot.com/2015/12/google-drive-uploading-downloading.html
#	http://wescpy.blogspot.com/2015/12/migrating-to-new-google-drive-api-v3.html

import os
import sys, getopt
from os import listdir
from os.path import isfile, join
from apiclient import discovery
from apiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools


DRIVE = None

MIME_TYPES = {
	"maff": "text/html",
	"srt": 'text/plain',
	"csv": 'text/plain',
	"xls" : 'application/vnd.ms-excel',
	"xlsx" : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
	"xml" : 'text/xml',
	"ods" : 'application/vnd.oasis.opendocument.spreadsheet',
	"tmpl" : 'text/plain',
	"pdf" : 'application/pdf',
	"php" : 'application/x-httpd-php',
	"jpg" : 'image/jpeg',
	"png" : 'image/png',
	"gif" : 'image/gif',
	"bmp" : 'image/bmp',
	"txt" : 'text/plain',
	"doc" : 'application/msword',
	"js" : 'text/js',
	"swf" : 'application/x-shockwave-flash',
	"mp3" : 'audio/mpeg',
	"zip" : 'application/zip',
	"rar" : 'application/rar',
	"tar" : 'application/tar',
	"arj" : 'application/arj',
	"cab" : 'application/cab',
	"html" : 'text/html',
	"htm" : 'text/html',
}


def get_mine_type(file_name):
	name, extension = os.path.splitext(file_name)
	extension = extension[1:]
	if extension in MIME_TYPES:
		return MIME_TYPES[extension]
	return None


def init():
	global DRIVE

	SCOPES = (
		'https://www.googleapis.com/auth/drive.file',
	)

	store = file.Storage('storage.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
		creds = tools.run_flow(flow, store)

	DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))


def display_files():
	# display files in the Google Drive
	DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))
	files = DRIVE.files().list().execute().get('files', [])
	for f in files:
		print(f['name'], f['mimeType'])


def create_folder(drive_service, name, parent_folder=None):
	metadata = {
	 'name' : name,
	 'mimeType' : 'application/vnd.google-apps.folder'
	}
	if parent_folder:
		metadata['parents'] = [parent_folder]
	folder = drive_service.files().create(
		body=metadata,
		fields='id'
	).execute()
	return folder.get('id')


def upload_file(drive_service, path, name, parent_folder=None, mime_type=None):
	metadata = {
		'name' : name,
	}
	if parent_folder:
		metadata['parents'] = [parent_folder]

	if not mime_type:
		mime_type = get_mine_type(name)

	if mime_type:
		metadata['mimeType'] = mime_type
		media = MediaFileUpload(path,
								mimetype=mime_type,
								resumable=True)
		file = drive_service.files().create(body=metadata,
											media_body=media,
											fields='id').execute()
	else:
		file = drive_service.files().create(body=metadata,
											media_body=path,
											fields='id').execute()
	return file.get('id')


# Download file
# if res:
#  MIMETYPE = 'application/pdf'
#  data = DRIVE.files().export(fileId=res['id'], mimeType=MIMETYPE).execute()
#  if data:
#  fn = '%s.pdf' % os.path.splitext(filename)[0]
#  with open(fn, 'wb') as fh:
#  fh.write(data)
#  print('Downloaded "%s" (%s)' % (fn, MIMETYPE))


# test_folder_id = create_folder(DRIVE, 'test folder')
# upload_file(DRIVE, 'hello.txt', 'hello.txt')
# upload_file(DRIVE, 'hello.txt', 'hello.txt', parent_folder=test_folder_id)


def upload_folder_recursive(path, parent_folder=None):
	path = os.path.realpath(path)
	dir_name = os.path.basename(os.path.normpath(path))
	dir_id = create_folder(DRIVE, dir_name, parent_folder=parent_folder)
	files = [f for f in listdir(path) if isfile(join(path, f))]
	folders = [f for f in listdir(path) if not isfile(join(path, f))]
	for f in files:
		upload_file(DRIVE, join(path, f), f, parent_folder=dir_id)
		print("File uploaded: %s" % join(path, f))
	for f in folders:
		upload_folder_recursive(join(path, f), parent_folder=dir_id)


def upload_folder(path):
	init()
	upload_folder_recursive(path)


def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hu:d:")
	except getopt.GetoptError:
		print('gdrive-manager.py -u <directory>')
		# print('gdrive-manager.py -d <directory>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print("Usage:")
			print(' gdrive-manager.py -u <directory>')
			print(' gdrive-manager.py -d <directory>')
			sys.exit()
		elif opt == '-u':
			upload_folder(arg)
		elif opt == '-d':
			print("Download")


if __name__ == "__main__":
	main(sys.argv[1:])