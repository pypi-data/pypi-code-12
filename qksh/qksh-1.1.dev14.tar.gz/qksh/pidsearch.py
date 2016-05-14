import os
import re


def find_inode():
    """
    :return inode: inode number for socket running on port 63333

    regex search for the local port equal F765, then return inode number
       sl local_address rem_address   ... inode
       0: 00000000:85EF 00000000:0000 ... 7817 1 ffff88007ae04700 100 0 0
       1: 0100007F:F765 00000000:0000 ... 151262 1 ffff88005b514700 100 0

    """
    with open('/proc/net/tcp', 'r') as f:
        f.readline()
        for line in f:
            if re.match(r'.*:F765$', line.split()[1]):
                inode = line.split()[9]
                return inode


# TODO: need to determine if the matched PID is qksh
# maybe from pid info?
def find_pid():
    """
    :return pid: pid number for the process runs over port 63333

    Get the inode number by parsing /proc/net/tcp at local_address column,

    /proc/net/tcp output:
       sl local_address rem_address   ... inode
       0: 00000000:85EF 00000000:0000 ... 7817 1 ffff88007ae04700 100 0 0
       1: 0100007F:F765 00000000:0000 ... 151262 1 ffff88005b514700 100 0

    a socket should bind to an inode in the format of socket:[inode number],
    e.g. socket:[151262].

    Then iter all the running process under /proc, looking up socket
    information under /proc/pid/fd/,

    (bash)# ls -la /proc/2080/fd/
    0  1  2  3  4  5  6  7
    (bash)# ls -la /proc/2080/fd/7
    lrwx------ 1 root root 64 Apr 16 13:53 /proc/2080/fd/7 -> socket:[151262]

    Once a match found, return the pid number. If no match found, return None.
    """
    inode = find_inode()

    procfiles = os.listdir('/proc/')
    # remove the pid of the current python process
    procfiles.remove(str(os.getpid()))
    pid_list = []

    for f in procfiles:
        try:
            integer = int(f)
            pid_list.append(str(integer))
        except ValueError:
            # if the filename doesn't convert to an integer, it's not a pid, 
            # and we don't care about it
            pass

    for pid in pid_list:
        for fd in os.listdir('/proc/{0}/fd/'.format(pid)):
            socket_inode_pattern = 'socket:[{inode}]'.format(inode=inode)
            proc_symbolic_link = os.readlink(
                '/proc/{pid}/fd/{fd}'.format(pid=pid, fd=fd))
            if socket_inode_pattern == proc_symbolic_link:
                return pid
