import six


def pack_gdb_command(command):
    command = command.encode('utf8')
    checksum = sum(six.iterbytes(command)) % 256
    return ('$%s#%2x' % (command, checksum)).encode('utf8')


if __name__ == '__main__':
    import pwny
    f = pwny.Flow.connect_tcp('localhost', 8888, echo=True)
    f.write(pack_gdb_command('s'))
    f.until('#')
    f.read(2)
