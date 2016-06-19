from setuptools import setup

setup(
	name='PyBeacon',
	version='0.2',
	packages=['PyBeacon'],
    entry_points = {
        "console_scripts": ['PyBeacon = PyBeacon.PyBeacon:main']
    },

    description ='Python script for scanning and advertising urls over Eddystone-URL.',

    url='https://github.com/nirmankarta/PyBeacon',

    download_url='https://github.com/nirmankarta/PyBeacon/archive/master.zip',

    author='Nirmankarta',

    author_email = 'we@nirmankarta.com',

    license='MIT',

    keywords = ['Eddystone', 'Eddystone URL', 'Beacon', 'Raspberry Pi'],

	classifiers=[
       
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',
    ],
)