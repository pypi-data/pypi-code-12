
from sys import exit as sys_exit
import logging
from fnmatch import fnmatch

def split_filelist(input_pattern, bed_files):

    chip_files, input_files = [], []
    input_pattern = "*" + input_pattern + "*"
    input_pattern = input_pattern.upper()
    for bed_file in bed_files:
        if fnmatch(bed_file.upper(), input_pattern):
            input_files.append(bed_file)
        else:
            chip_files.append(bed_file)

    if len(chip_files) == 0:
        logging.error("All files considered input. This means all your files match the"
                      " case insensitive pattern: " + input_pattern)
        sys_exit(1)
    if len(input_files) == 0:
        logging.error("No input files found. This means none of your files match"
                      " the case insensitive pattern: " + input_pattern)
        sys_exit(1)

    return chip_files, input_files
