#!/usr/bin/python
import os
import glob
import getopt
import sys
import subprocess
import json
from os.path import basename
from PIL import Image
import picture


def load_file(file_name):
    picture_obj = picture.Picture(file_name)
    if picture_obj.check_extensions():
        info_text = """
    OPENED FILE:
    {}
    SIZE
    {}
    RESOLUTION
    {}
    ORIENTATION
    {}
    BITS
    {}
    IS COLORED
    {}
    DOMINANT COLORS
    {}
    EXIF
    {}
    SUCCES
     """.format(basename(file_name),
                picture_obj.get_size(),
                picture_obj.get_resolution(),
                picture_obj.get_orientation(),
                picture_obj.get_bits(),
                picture_obj.get_is_colored(),
                picture_obj.get_dominant_colors(),
                picture_obj.get_exif())
        print(info_text)
    else:
        print('Unsupported extension', basename(file_name))


def load_text(text_name):
    if text_name.endswith('.txt'):
        with open(text_name) as input_file:
            for line in input_file:
                load_file(line)
    else:
        print('Unsupported extension. Try to use .txt files')


def load_folder(folder_path):
    for file_name in os.listdir(folder_path):
        load_file(os.path.join(folder_path, file_name))


def json_output(input_file):
    picture_obj = picture.Picture(input_file)
    serialized_data = json.dumps({
        '1.size': picture_obj.get_size(),
        '2.resolution': picture_obj.get_resolution(),
        '3.orientation': picture_obj.get_orientation(),
        '4.bits': picture_obj.get_bits(),
        '5.iscolored': picture_obj.get_is_colored(),
        '6.dominant_colors': picture_obj.get_dominant_colors(),
        '7.EXIF': picture_obj.get_exif()
        }, sort_keys=True, indent=4, separators=(',', ': '))
    with open('output.txt', 'w+') as text_file:
        text_file.write(serialized_data)
        text_file.close()


def main(argv):
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'h:i:d:l:c:o',
            ['help', 'image=', 'dir=', 'list=', 'console', 'output=']
            )
    except getopt.GetoptError:
        print('image.py --image <file.jpg> ')
        print('--dir <path_of_file>, --list <file.txt>,')
        print('--console, --output <file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in('-h', '--help'):
            print('Syntax:image.py [OPTION]  ... [FILE]')
            print('Arguments:')
            print('--help 		        display this help and exit ')
            print('-i, --image		write processing result of single file')
            print('-d, --dir		write processing result of files from dir ')
            print('-l, --list		write processing result of files ')
            print('                        from pathes saved in text file')
            print('-c, --console	        show commandline user interface')
            print('-o, -- output	        output the JSON of single file')
            sys.exit()
        elif opt in ('-i', '--image'):
            input_file_name = arg
            load_file(input_file_name)
        elif opt in ('-d', '--dir'):
            input_file_name = arg
            load_folder(os.path.join(os.getcwd(), input_file_name))
        elif opt in ('-l', '--list'):
            input_file_name = arg
            load_text(os.path.join(os.getcwd(), input_file_name))
        elif opt in ('-c', '--console'):
            print('1.load one file')
            print('2.load all form folder')
            print('3.load all paths from *txt')
            print('4.end')

            choice = input('choose choice> ')
            if choice == '1':
                file = input('relative path of file ')
                load_file(file)
            elif choice == '2':
                files = input('relative path to folder')
                load_folder(files)
            elif choice == '3':
                files = input('relative path to text with ')
                load_text(files)
            elif choice == '4':
                print('program stopped')
                return

            else:
                print('wrong choice program exit')
                return
        elif opt in ('-o', '--output'):
            input_file = arg
            json_output(arg)
if __name__ == '__main__':
    main(sys.argv[1:])
