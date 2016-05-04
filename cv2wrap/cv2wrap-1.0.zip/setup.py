from distutils.core import setup
setup(
  name = 'cv2wrap',
  packages = ['cv2wrap'], # this must be the same as the name above
  version = '1.0',
  description = 'Wrapper for python opencv 2.4.12 32bit',
  author = 'Lucas V. Oliveira',
  author_email = 'lucas.o@live.com',
  url = 'https://github.com/lucasolivier/cv2wrap', # use the URL to the github repo
  download_url = 'https://github.com/lucasolivier/cv2wrap/tarball/1.0', # I'll explain this in a second
  keywords = ['opencv', 'cv2', 'python'], # arbitrary keywords
  classifiers = []
)


#setup(name='cv2',
      #version='1.0',
      #py_modules=['cv2'],
      #)


#setup_args = { 
 # 'name': 'cv2wrap',
 # 'packages': ['cv2wrap'], # this must be the same as the name above
 # 'version': '1.0',
 # 'description': 'Wrapper for python opencv 2.4.12 32bit',
 # 'author': 'Lucas V. Oliveira',
 # 'author_email': 'lucas.o@live.com',
 # 'url': 'https://github.com/lucasolivier/cv2wrap', # use the URL to the github repo
 # 'download_url': 'https://github.com/lucasolivier/cv2wrap/tarball/1.0', # I'll explain this in a second
 # 'keywords': ['opencv', 'cv2', 'python'], # arbitrary keywords
#  'classifiers': []

#}
#if True:
    #class my_build_ext():
        #def build_extension(self, ext):
            #''' Copies the already-compiled pyd
            #'''
            #import shutil
            #import os.path
            #try:
                #os.makedirs(os.path.dirname(self.get_ext_fullpath(ext.name)))
            #except WindowsError, e:
                #if e.winerror != 183: # already exists
                    #raise


            #shutil.copyfile(os.path.join(this_dir, r'..\..\bin\Python%d%d\my.pyd' % sys.version_info[0:2]), self.get_ext_fullpath(ext.name))

    #setup_args['cmdclass'] = {'build_ext': my_build_ext }

#setup(**setup_args)