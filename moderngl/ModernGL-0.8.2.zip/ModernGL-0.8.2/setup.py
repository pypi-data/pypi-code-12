from distutils.core import setup, Extension

PyModernGL = Extension(
	'PyModernGL',
	# include_dirs = ['/usr/local/include'],
	libraries = ['User32'],
	# library_dirs = ['/usr/local/lib'],
	sources = [
		'Source/WindowsGL.cpp',
		'Source/OpenGL.cpp',
		'Source/ModernGL.cpp',
		'Source/Python-ModernGL.cpp',
	]
)

setup(
	name = 'ModernGL',
	version = '0.8.2',
	description = 'ModernGL',
	url = 'https://github.com/cprogrammer1994/Python-ModernGL',
	author = 'Szabolcs Dombi',
	author_email = 'cprogrammer1994@gmail.com',
	license = 'APACHE',
	packages = [],
	ext_modules = [PyModernGL]
)
