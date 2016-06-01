import os
import fnmatch
import hashlib
import subprocess

from generaltools import log_tools

def find_files_by_ending_in_directory(ending, directory):
    """Return paths to all files with `ending` in subfolders of `directory`"""
    file_list = [os.path.join(dirpath, f)
                 for dirpath, dirnames, files in os.walk(directory)
                 for f in fnmatch.filter(files, "*.{}".format(ending))]
    return file_list

def hash_file(path_to_file):
    """ Returns the MD5 Sum of a file"""
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(path_to_file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

class Rsync(object):
    ''' Wrapper around the Rsync command'''
    def __init__(self, source=None, target=None, exclude_file=None,
                 options=None, delete=False, use_ssh=False):
        self.log = log_tools.init_logger("rsync")
        self.rsync_path = "/usr/bin/rsync"
        if not os.path.isfile(self.rsync_path):
            self.log.error("Can't find rsync under {}".format(self.rsync_path))
            raise SystemExit
        self.source = source
        self.target = target
        self.exclude_file = exclude_file
        self.options = options
        self.delete = delete
        self.use_ssh = use_ssh
        self.command = self.create_rsync_command()

    def add_crucial_rsync_parts(self, part):
        '''This function can be used to add components to the command string
        that have to be set.
        '''
        if part:
            return "{}".format(part)
        else:
            raise ValueError

    def create_rsync_command(self):
        command= []
        command += [self.rsync_path]
        if self.options:
            option_list = self.options.split()
            if len(option_list) > 1:
                for entry in option_list:
                    if not entry.startswith("-"):
                        raise ValueError
                minus  = ""
            else:
                if not self.options.startswith("-"):
                    minus  = "-"
                else:
                    minus = ""
            command += ["{}{}".format(minus, self.options)]
        if self.exclude_file:
            command += ["--exclude-from={}".format(self.exclude_file)]
        if self.use_ssh:
            command += ["-e \"ssh -i /home/$USER/.ssh/id_rsa\""]
        if self.delete:
            command += ["--delete"]
        command += [self.add_crucial_rsync_parts(self.source)]
        command += [self.add_crucial_rsync_parts(self.target)]
        return command

    def execute(self):
        subprocess.check_call(self.command)
