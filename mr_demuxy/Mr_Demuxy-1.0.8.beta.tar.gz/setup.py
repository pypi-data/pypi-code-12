
import os


from distutils.core import setup


def file_path_joiner(file_dir):
    files_list = os.listdir(file_dir)
    corrected_file_path = []
    for cur_file in files_list:
        cur_fp = os.path.join(file_dir, cur_file)
        corrected_file_path.append(cur_fp)
    return corrected_file_path

script_files = file_path_joiner('bin')



setup(
    name = 'Mr_Demuxy',
    version = '1.0.8.beta',
    description = 'demultiplexs combinatorially tagged reads',

    author = 'Daniel E. Lefever',
    author_email = 'lefeverde@gmail.com',
    
    packages = ['Mr_Demuxy'],
    package_dir = {
    'Mr_Demuxy': 'mr_demuxy',
    },
    scripts = script_files,

    package_data = {
    'Mr_Demuxy': ['example_data/example*'],
    'Mr_Demuxy': ['example_data/*.txt']
    },    
    data_files = [
    ('Mr_Demuxy', ['MANIFEST.in']),
    ('', ['LICENSE/biopython_license.txt'])],
    
    license = 'MIT',

    platforms = 'any',
    classifiers = [
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        ]
    
    
    )