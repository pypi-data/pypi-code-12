import distutils.msvccompiler
# from distutils.core import setup
# from distutils.extension import Extension
from setuptools import setup, Extension

import os, sys, platform

if 'CUSTOM_GCC' in os.environ:
	class CustomCCompiler:
		def __init__(self, verbose = 0, dry_run = 0, force = 0):
			self.comp = 'g++ -m%s' % platform.architecture()[0][:2]
			self.compiler_type = None

		def set_include_dirs(self, dirs):
			print('set_include_dirs:', dirs)
			self.inc_dirs = dirs.copy()
			# self.pydll = 

		def set_libraries(self, *args):
			print('set_libraries:', args)

		def set_library_dirs(self, *args):
			print('set_library_dirs:', args)

		def set_runtime_library_dirs(self, *args):
			print('set_runtime_library_dirs:', args)

		def compile(self, sources, *args, **kwargs):
			print('compile:', args, kwargs)
			output_dir = kwargs['output_dir']
			if not os.path.isdir(output_dir):
				os.makedirs(output_dir)

			objects = []
			for source in sources:
				print('\n' * 10)
				print(source)
				output_base = os.path.basename(source)
				output_name = os.path.splitext(output_base)[0]
				output_filename = os.path.join(output_dir, output_name + '.o')
				incs = ' '.join('-I %s' % inc for inc in self.inc_dirs)
				os.system('%s -c %s %s -o %s' % (self.comp, incs, source, output_filename))
				objects.append(output_filename)

			return objects

		def detect_language(self, *args):
			print('detect_language:', args)
			
		def link_shared_object(self, objects, output_filename, *args, **kwargs):
			print('link_shared_object:', args, kwargs)

			output_dir = os.path.dirname(output_filename)
			if not os.path.isdir(output_dir):
				os.makedirs(output_dir)

			build_temp = kwargs['build_temp']
			if not os.path.isdir(build_temp):
				os.makedirs(build_temp)

			output_base = os.path.basename(output_filename)
			output_name = os.path.splitext(output_base)[0]
			def_filename = os.path.join(build_temp, output_name + '.def')

			def_file = open(def_filename, 'w')
			def_file.write('LIBRARY %s.pyd\n' % output_name)
			def_file.write('EXPORTS\n')
			def_file.write('\n'.join(kwargs['export_symbols']))
			def_file.close()

			libs = ' '.join('-l%s' % lib for lib in kwargs['libraries'])
			objs = ' '.join(objects)

			print('\n' * 10)
			dll = 'python%d%d.dll' % (sys.hexversion >> 24, (sys.hexversion >> 16) & 0xff)
			pydll = os.path.join(os.path.dirname(sys.executable), dll)
			print(pydll)

			os.system('%s -shared -O2 %s %s %s %s -o %s' % (self.comp, def_filename, objs, libs, pydll, output_filename))


	# distutils.ccompiler.CCompiler = CustomCCompiler
	distutils.msvccompiler.MSVCCompiler = CustomCCompiler

ShortDescription = 'modern OpenGL binding for Python'

LongDescription = '''
OpenGL is a great environment for developing portable, platform independent,
interactive 2D and 3D graphics applications. The API implementation in Python
is cumbersome, resulting in applications with high latency. To solve this
problem we have developed ModernGL, a wrapper over OpenGL that simplifies the
creation of simple graphics applications like scientific simulations, small
games or user interfaces. Usually, acquiring in-depth knowledge of OpenGL
requires a steep learning curve. In contrast, ModernGL is easy to learn and
use, moreover it is capable of rendering with the same performance and
quality, with less code written.
'''

Classifiers = [
	'Development Status :: 4 - Beta',
#	'Development Status :: 5 - Production/Stable',
#	'Development Status :: 6 - Mature',
	'Environment :: Win32 (MS Windows)',
	'Intended Audience :: Developers',
	'Intended Audience :: Education',
	'License :: Free For Educational Use',
	'License :: Free For Home Use',
	'License :: Freeware',
	'License :: OSI Approved :: MIT License',
	'Natural Language :: English',
	'Operating System :: Microsoft :: Windows',
	'Operating System :: Microsoft :: Windows :: Windows 3.1 or Earlier',
	'Operating System :: Microsoft :: Windows :: Windows 7',
	'Operating System :: Microsoft :: Windows :: Windows 95/98/2000',
	'Operating System :: Microsoft :: Windows :: Windows CE',
	'Operating System :: Microsoft :: Windows :: Windows NT/2000',
	'Operating System :: Microsoft :: Windows :: Windows Server 2003',
	'Operating System :: Microsoft :: Windows :: Windows Server 2008',
	'Operating System :: Microsoft :: Windows :: Windows Vista',
	'Programming Language :: C++',
	'Programming Language :: Python',
	'Programming Language :: Python :: 3.3',
	'Programming Language :: Python :: 3.4',
	'Programming Language :: Python :: 3.5',
	'Programming Language :: Python :: 3.6',
	'Programming Language :: Python :: 3 :: Only',
	'Topic :: Desktop Environment',
	'Topic :: Education',
	'Topic :: Games/Entertainment',
	'Topic :: Multimedia',
	'Topic :: Multimedia :: Graphics',
	'Topic :: Multimedia :: Graphics :: 3D Modeling',
	'Topic :: Multimedia :: Graphics :: 3D Rendering',
	'Topic :: Scientific/Engineering :: Visualization',
	'Topic :: Software Development',
	'Topic :: System :: Monitoring',
	'Topic :: Utilities',
]

Keywords = [
	'ModernGL',
	'modern OpenGL',
	'OpenGL',
	'GL',
	'GLEXT',
	'GLU',
	'ARB',
	'2D',
	'3D',
	'graphics',
	'cad',
]

ModernGL = Extension(
	'ModernGL.ModernGL',
	libraries = ['user32', 'gdi32'],
	sources = [
		'Source/WindowsGL.cpp',
		'Source/OpenGL.cpp',
		'Source/ModernGL.cpp',
		'Source/Python-ModernGL.cpp',
	]
)

setup(
	name = 'ModernGL',
	version = '2.0.9',
	description = ShortDescription,
	long_description = LongDescription,
	url = 'https://github.com/cprogrammer1994/ModernGL',
	author = 'Szabolcs Dombi',
	author_email = 'cprogrammer1994@gmail.com',
	license = 'MIT',
	classifiers = Classifiers,
	keywords = Keywords,
	packages = ['ModernGL'],
	ext_modules = [ModernGL],
	platforms = ['win32', 'win64']
)
