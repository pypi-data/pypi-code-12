# import the wonderful requests lib
# if you need to intall it just try
# pip install --upgrade requests
import requests

# define where is your py3o.fusion endpoint
url = 'http://localhost:8765/form'

# open up the file and stuff it into a dictionary
# tmpl_file is a required field on the form. If you don't give
# it to the endpoint you'll receive an error back from it.
files = {
    'tmpl_file': open('templates/simple.odt', 'rb')
}

# then prepare the other fields of the form
# those 3 fields are also mandatory and failing to POST
# one of them will get you an error back from the server
#
# In this example you can see we leave the datadictionary
# and the image_mapping empty... This is because we won't
# send a template to the server but a simple plain
# old ODT file
fields = {
    "targetformat": 'pdf',
    "datadict": "{}",
    "image_mapping": "{}",
}

# finally POST our request on the endpoint
r = requests.post(url, data=fields, files=files)

# don't forget to close our orginal odt file
files['tmpl_file'].close()

# see if it is a success or a failure
# ATM the server only returns 400 errors... this may change
if r.status_code == 400:
    # server says we have an error...
    # this means it properly catched the error and nicely
    # gave us some info in a JSON answer...
    # let's use this fact
    print r.json()

else:
    # if we're here it is because we should receive a new
    # file back

    # let's stream the file back here...
    chunk_size = 1024

    # fusion server will stream an ODT file content back
    outname = 'request_out.%s' % 'pdf'
    with open(outname, 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)

    # warn our dear user his file is ready
    print "Your file: %s is ready" % outname
