#SFTP Master
import os, tarfile, paramiko
from stat import S_ISDIR


class SFTApi(object):

    transport = None
    sftp = None
    zipname = None

    def __init__(self, *args, **kwargs):
        self.hostname = kwargs['FTP_DOMAIN']
        self.port = kwargs['FTP_PORT']
        self.username = kwargs['FTP_USERNAME']
        self.password = kwargs['FTP_PASSWORD']
        self._connect()

    def _connect(self, *args, **kwargs):
        """ It is used to connect with remote host """
        self._get_ssh()
        self.transport = paramiko.Transport((self.hostname, self.port))
        self.transport.connect(username = self.username, password = self.password)
        
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        print "Connected to ", self.hostname, "as ", self.username
        return

    def _get_ssh(self, *args, **kwargs):
        """ It is used to connect as ssh """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, username = self.username, password = self.password)
        return ssh

    
    def isExists(self, path):
        """ It will return whether a file/directory exists or not and return type """
        """ 1 - directory, 0 - file, -1 - Not exists """
        is_file = os.path.isfile(path)
        is_dir = os.path.isdir(path)

        if is_file or is_dir:
            if is_file:
                return 0
            else:
                return 1
        else:
            return -1

    def remove(self, path):
        self.sftp.remove(path)


    def upload(self, *args, **kwargs):
        """ It is used to upload files / folders """
        if "source" and "destination" not in kwargs:
            return
        else:
            path_type = self.isExists(kwargs['source'])
            if path_type == -1:
                return 
            if path_type == 0:
                #Copy directly
                file_name = kwargs['source'].split("/")[len(kwargs['source'].split("/")) -1]
                self.sftp.put(kwargs['source'], kwargs['destination'] + file_name)
            if path_type == 1:
                #  recursively upload a full directory
                os.chdir(os.path.split(kwargs['source'])[0])
                parent=os.path.split(kwargs['source'])[1]
                for walker in os.walk(parent):
                    try:
                        self.sftp.mkdir(os.path.join(kwargs['destination'],walker[0]))
                    except:
                        pass
                    for file in walker[2]:
                        self.sftp.put(os.path.join(walker[0],file),os.path.join(kwargs['destination'],walker[0],file))
        return 
    def sftp_walk(self,remotepath):
        # Kindof a stripped down  version of os.walk, implemented for 
        # sftp.  Tried running it flat without the yields, but it really
        # chokes on big directories.
        path = remotepath
        files = []
        folders = []
        for f in self.sftp.listdir_attr(remotepath):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        yield path,folders,files
        for folder in folders:
            new_path=os.path.join(remotepath,folder)
            for x in self.sftp_walk(new_path):
                yield x


    def download(self, *args, **kwargs):
        """ It is used to download the file / folders """
        if "source" and "destination" not in kwargs:
            return
        else:
            if 'type' not in kwargs or kwargs['type'] == "File":
                self.sftp.get(kwargs['source'], kwargs['destination'] + kwargs['source'].split("/")[-1])
            else:
                self.sftp.chdir(os.path.split(kwargs['source'])[0])
                parent = os.path.split(kwargs['source'])[1]
                try:
                    os.mkdir(kwargs['destination'])
                except:
                    pass
                for walker in self.sftp_walk(parent):
                    try:
                        os.mkdir(os.path.join(kwargs['destination'],walker[0]))
                    except:
                        pass
                    for file in walker[2]:
                        
                        try:
                            self.sftp.get(os.path.join(walker[0],file),os.path.join(kwargs['destination'],walker[0],file))
                        except:
                            pass
        return

    
