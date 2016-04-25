"""This module defines the functions SCRY uses to write log files of the HTTP requests it handles.
The directory where log files are saved can be configured in :mod:`scry`.\ :mod:`__init__.py`.

.. todo: Expand logging functionality, e.g. with (multiple levels of) debug support"""

import os
import datetime
import pkg_resources as pkr
from shutil      import copyfile
from scry.config import get_subdir

def make_link(link,target):
    if os.path.isfile(link): os.remove(link)
    if getattr(os,'symlink',None):
        os.symlink(target,link)
    else:
        from subprocess import call
        call(['mklink', link, target], shell=True)


def get_runtime_log():
    "Returns a function that will append a timestamp and the value of `msg` to the specified file -- typically a live instance's runtime log."
    # Define the appending function
    t = datetime.datetime.now().isoformat()[:-7]
    log_file = os.path.join(get_subdir('Logs','runtime'),'%s.log' % t.replace(':','.'))
    def log(msg):
        with open(log_file,'a') as f:
            f.write('%s - %s\n' % (str(datetime.datetime.now()),msg))

    # Make the file and update last_runtime.log:
    open(log_file,'w').close()
    last_log = os.path.join(get_subdir('Logs'),'last_runtime.log')
    make_link(last_log,log_file)
    return log


def log_request(request):
    "Writes a logfile documenting a received HTTP request, named after the date and time said request was received."
    t         = datetime.datetime.now()    
    date      = t.date().isoformat()
    time      = t.time().isoformat()
    dir_path  = os.path.join(get_subdir('Logs','requests'),date)
    file_path = os.path.join(dir_path,'%s.log' % (time.replace(':','.')))
    pkr.ensure_directory(file_path)
    spacer    = '\n\n----------\n\n'
        
    vals = request.values
    print 'Logging SPARQL request ('+time+')'
    with open(file_path,'w') as f:
        f.write('Method   :\t'+request.method+'\n')
        f.write('Time     :\t'+time+'\n')
        f.write('Base URL :\t'+request.base_url+'\n')
        f.write('Full Path:\t'+request.full_path+spacer)
        f.write('Values (Len '+str(len(vals))+'):'+'\t'+str(vals) + '\n')

        for k in vals:
            f.write('\n'+k+':\t'+vals[k])
        f.write(spacer)
        f.write('Content Length     :\t'+str(request.content_length)+'\n')
        f.write('Content Type       :\t'+str(request.content_type)+'\n')
        f.write('Accepted Response Types:\t'+str(request.accept_mimetypes)+spacer)

        f.write(str(dir(request)) + spacer)
        for prop in dir(request):

            if prop.find('__') != -1: continue
            elif prop == 'access_route': continue # Not sure why, but not skipping this causes issues
            
            f.write('=== ' + prop + ' ===\n\n')
            val = getattr(request,prop)
            fnc = hasattr(val,'__call__')
            if fnc:
                f.write(str(type(val)) + spacer)
            else:
                f.write(str(val) + spacer)

    # Make last_request.log a link to the appropriate location
    last_path = os.path.join(get_subdir('Logs'),'last_request.log')
    make_link(last_path,file_path)
    
    return date, time


def log_response(response, date, time):
    "Writes a logfile documenting the response to a received HTTP request, named after the date and time said request was received."
    
    print 'Logging SPARQL response ('+time+')'
    dir_path  = os.path.join(get_subdir('Logs','responses'),date)
    file_path = os.path.join(dir_path,'%s.log' % (time.replace(':','.')))
    pkr.ensure_directory(file_path)
    with open(file_path,'w') as f:
        f.write(response)

    # Make last_response.log a link to the appropriate location
    last_path = os.path.join(get_subdir('Logs'),'last_response.log')
    make_link(last_path,file_path)