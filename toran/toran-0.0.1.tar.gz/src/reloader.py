#! /usr/bin/python
import mmap


def main():
    """
    Will mark a status file to tell the server to reload the configs
    :return:
    """
    local_file = open('.status', 'r+')
    local_file.truncate(1)
    status_file = mmap.mmap(local_file.fileno(), 1, mmap.MAP_SHARED, mmap.PROT_WRITE)
    status_file.write_byte('1')
    status_file.flush()

if __name__ == '__main__':
    """
    Launches the main method to alter shared memory file
    """
    main()