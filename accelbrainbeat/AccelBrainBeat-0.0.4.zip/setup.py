#!/user/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='AccelBrainBeat',
    version='0.0.4',
    description='This python script enables you to handle your mind state by a kind of "Brain-Wave Controller" which is generally known as Biaural beat or Monaural beat in a simplified method.',
    long_description='The function of this library is inducing you to be extreme immersive mind state on the path to peak performance. You can handle your mind state by using this library which is able to control your brain waves by the binaural beat and the monaural beat.',
    url='https://github.com/chimera0/Binaural-Beat-and-Monaural-Beat-with-python',
    author='chimera0',
    author_email='kimera0kimaira@gmail.com',
    license='GPL2',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3',
    ],
    keywords='binaural monaural beat brain wave',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['numpy', 'PyAudio'],
)
