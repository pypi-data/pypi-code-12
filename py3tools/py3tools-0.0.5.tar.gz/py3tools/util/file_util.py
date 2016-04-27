class FileUtil:

    @staticmethod
    def write_file(file_name, message):
        f = open(file_name, 'wb')
        f.write(message)
        f.close()