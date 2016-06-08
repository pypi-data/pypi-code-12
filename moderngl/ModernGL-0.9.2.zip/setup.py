from setuptools import setup, Extension

ModernGL = Extension(
	'ModernGL.ModernGL',
	libraries = ['User32'],
	sources = [
		'Source/WindowsGL.cpp',
		'Source/OpenGL.cpp',
		'Source/ModernGL.cpp',
		'Source/Python-ModernGL.cpp',
	]
)

setup(
	name = 'ModernGL',
	version = '0.9.2',
	description = 'ModernGL',
	url = 'https://github.com/cprogrammer1994/ModernGL',
	author = 'Szabolcs Dombi',
	author_email = 'cprogrammer1994@gmail.com',
	license = 'MIT',
	packages = ['ModernGL'],
	ext_modules = [ModernGL],
	platforms = ['win32', 'win64']
)
