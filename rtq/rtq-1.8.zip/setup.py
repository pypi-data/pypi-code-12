from setuptools import setup

setup(
	name='rtq',
	version = '1.08',
	url = 'https://github.com/nhsb1/yf-realtime',
	scripts=['rtqinfo.py'],
	install_requires=['lxml','beautifulsoup4', 'yahoo_finance', 'BeautifulSoup', 'argparse', 'urllib3', 'colorama'])
 


