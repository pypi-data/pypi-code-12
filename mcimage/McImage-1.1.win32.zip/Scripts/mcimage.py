#!/usr/bin/env python3

import sys
import requests
import bs4
import os
import urllib
import logging
from time import gmtime, strftime
from os.path import expanduser
from optparse import OptionParser

def main():
    VERSION = '1.0 Beta'
    try:

        if os.path.isdir(expanduser('~/Pictures')):
            HOME = expanduser('~/Pictures')
        else:
            if os.path.isdir(os.path.join(os.environ["HOME"], 'Pictures')):
                HOME = os.path.join(os.environ["HOME"], 'Pictures')
            else:
                if os.path.isdir(os.path.join(expanduser('~'),'Pictures')):
                    HOME = os.path.join(expanduser('~'),'Pictures')
                else:
                    if os.path.isdir(expanduser('~')):
                        os.mkdir(os.path.join(expanduser('~'), 'Pictures'))
                        if os.path.isdir(os.path.join(expanduser('~'),'Pictures')):
                            print('Pictures directory created.')
                            HOME = os.path.join(expanduser('~'),'Pictures')
                    else:
                        if os.path.isdir(os.environ["HOME"]):
                            os.mkdir(os.path.join(os.environ["HOME"], 'Pictures'))
                            if os.path.isdir(os.path.join(os.environ["HOME"], 'Pictures')):
                                print('Pictures directory created.')
                                HOME = os.path.join(os.environ['HOME'], 'Pictures')
        
        if not os.path.isdir(os.path.join(HOME, 'McImage')):
            os.mkdir(os.path.join(HOME, 'McImage'))
            if os.path.isdir(os.path.join(HOME, 'McImage')):
                PATH = os.path.join(HOME, 'McImage')
                print('McImage download directory created ({0})'.format(PATH))
        else:
            PATH = os.path.join(HOME, 'McImage')
                             

        usage = '''
%prog url [options] -d -f -n -m --directory --folder --filename --mode

example: '%prog http://4chan.org/co/somethread' would download all images from http://4chan.org/co/somethread and save to the default directory({0}).

example: '%prog http://4chan.org/co/somethread -d C://Users/somename -f Hulkphotos -n Hulk' would download images and save to {0}/Hulkphotos as Hulk[x].jpg'''.format(PATH)
        parser = OptionParser(usage=usage, version='%prog {0}'.format(VERSION))
        
        parser.add_option('-d', '--directory', action='store', type='string', dest='loc', help='allows user to enter filepath for desired local download direcory')
        parser.add_option('-f', '--folder', action='store', type='string', dest='folder', help='allows user to specify a folder/directory name for downloads')
        parser.add_option('-n', '--filename', action='store', type='string', dest='filename', help='allows user to specify how images will be named')
        parser.add_option('-m', '--mode', action='store', type='string', dest='mode', help='allows the user to select different modes(-m 4chan for example)')
        (options, args) = parser.parse_args()

        if len(args) !=1:
            print('''
McImage launched in manual mode, either no arguments were given or the program executable was launched manually.
Manual mode only allows for basic usage of the McImage software. For more information run 'mcimage -h' from command line.''')
            url = input('please enter the url of the site you would like to download images from: ').strip(' ')
        else:
            for arg in args:
                if 'http://' in(arg) or 'https://' in(arg):
                    url = arg
                else:
                    logging.error('Please enter the full url including the "http:// or https://"')
					sys.exit(2)
        loc=options.loc
        folder=options.folder
        filename=options.filename
        mode=options.mode
        
        
        
        time = strftime("%y%m%d%H%M%S", gmtime())
        if loc is None:
            loc = PATH
        else:
            if os.path.isdir(loc):
                print('Directory valid')
            else:
                logging.error('Directory given({0}) is not a directory, changing directory to {1}.'.format(loc, PATH))
                loc = PATH
        if folder is None:
            os.mkdir('{0}/{1}'.format(loc, time))
            folder = '{0}/{1}'.format(loc, time)
        else:
            if not os.path.isdir('{0}'.format(os.path.join(loc, folder))):
                os.mkdir('{0}'.format(os.path.join(loc, folder)))
                if os.path.isdir('{0}'.format(os.path.join(loc, folder))):
                    print('Directory created')
            
        
        res = requests.get(url)
        soups = bs4.BeautifulSoup(res.text, 'html.parser')
        if mode is None:
            imgs = soups.select('img[src]')
        elif mode =='4chan':
            imgs = soups.select('img[src*="//i.4cdn.org/"]')
        else:
            logging.error('The mode you selected is invalid, defaulting to normal mode')
            imgs = soups.select('img[src]')
        
        Derrors = 0
        downs = 0
        for image in range(len(imgs)):
            if not(imgs[image]['src']).startswith('http:') or not(imgs[image]['src']).startswith('https:'):
                urlstart = 'http:'
            else:
                urlstart = ''
            urllib.request.urlcleanup()
            try:
                if filename is None:
                    try:
                        urllib.request.urlretrieve(urlstart+imgs[image]['src'], '{0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                        print('http:'+imgs[image]['src']+' image saved as {0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                        downs+=1
                    except Exception:
                        try:
                            urllib.request.urlretrieve('https:'+imgs[image]['src'], '{0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                            print('http:'+imgs[image]['src']+' image saved as {0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                            downs+=1
                        except Exception as e:
                            logging.error('{0} \nerror downloading http:'.format(e)+imgs[image]['src'])
                            Derrors+=1
                        
                else:
                    if not os.path.isfile('{0}{1}.jpg'.format(os.path.join(loc, folder, filename), image)):
                        try:
                            urllib.request.urlretrieve(urlstart+imgs[image]['src'], '{0}{1}.jpg'.format(os.path.join(loc, folder, filename), image))
                            print('http:'+imgs[image]['src']+' image saved as {0}{1}.jpg'.format(os.path.join(loc, folder, filename), image))
                            downs+=1
                        except Exception:
                            try:
                                urllib.request.urlretrieve('https:'+imgs[image]['src'], '{0}{1}.jpg'.format(os.path.join(loc, folder, filename), image))
                                print('http:'+imgs[image]['src']+' image saved as {0}{1}.jpg'.format(os.path.join(loc, folder, filename), image))
                                downs+=1
                            except Exception as e:
                                logging.error('{0} \nsomething went wrong, trying to save images with default naming scheme.'.format(e))
                                try:
                                    urllib.request.urlretrieve(urlstart+imgs[image]['src'], '{0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                                    print('http:'+imgs[image]['src']+' image saved as {0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                                    downs+=1
                                except Exception:
                                    try:
                                        urllib.request.urlretrieve('https:'+imgs[image]['src'], '{0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                                        print('http:'+imgs[image]['src']+' image saved as {0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                                        downs+=1
                                    except Exception as e:
                                        Derrors += 1
                                        logging.error('\nerror saving file, source: http:'+imgs[image]['src'])
                    else:
                        print('{0}{1}.jpg already exists, using default filename.'.format(os.path.join(loc, folder), image))
                        try:
                            urllib.request.urlretrieve(urlstart+imgs[image]['src'], '{0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                            print('http:'+imgs[image]['src']+' image saved as {0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                            downs+=1
                        except Exception:
                            try:
                                urllib.request.urlretrieve('https:'+imgs[image]['src'], '{0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                                print('http:'+imgs[image]['src']+' image saved as {0}/image{1}.jpg'.format(os.path.join(loc, folder), image))
                                downs+=1
                            
                            except Exception as e:
                                Derrors += 1
                                logging.error('\nerror saving file, source: http:'+imgs[image]['src'])
            except Exception as e:
                Derrors += 1
                logging.error('{0} \nerror downloading http:'.format(e)+imgs[image]['src'])
        if Derrors:
            print('\n{0} image(s) downloaded successfully'.format(downs))
            print('{0} image(s) not downloaded'.format(Derrors))
        else:
            print('\nAll image(s) downloaded successfully, image(s) retrieved: {0}'.format(downs))
    except KeyboardInterrupt:
        print('Ctrl-C')
        print('Operation halted')
        sys.exit
    except Exception as e:
        logging.error('{0} \nSomething went wrong!!'.format(e))





if __name__ == "__main__":
    main()

