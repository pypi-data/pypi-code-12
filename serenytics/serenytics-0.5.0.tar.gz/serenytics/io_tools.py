import paramiko


def connect_to_sftp_server(username, password, hostname, port):
    t = paramiko.Transport((hostname, port))
    t.connect(username=username, password=password)
    return paramiko.SFTPClient.from_transport(t)
