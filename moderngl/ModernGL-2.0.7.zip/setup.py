from setuptools import setup, Extension

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
	version = '2.0.7',
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
