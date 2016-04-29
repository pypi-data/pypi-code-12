from pneumatic import DocumentCloudUploader

client = DocumentCloudUploader('anthony@documentcloud.org', 'Ball1h00fa11s')
#client.upload(project='17477-loudoun-county-government')
# print client.username


# import sys
# import glob
# from documentcloud import DocumentCloud
# from db.db import Database

# # instantiate client, database
# client = DocumentCloud('anthony@documentcloud.og', 'Ball1h00fa11s')
# db = Database('test')

# # properties

# project_id = '17477-loudoun-county-government'
# description = 'a document description'
# title = 'python-documentcloud test'

# # get files
# files = glob.glob('files/*')

# for f in files:
#     doc = open(f, 'rb')
#     try:
#         print 'Uploading ' + doc.name
#         obj = client.documents.upload(doc, project=project_id)
#         print obj.title
#     except:
#         print sys.exc_info()[0]
