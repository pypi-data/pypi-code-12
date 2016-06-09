import subprocess
import os


def shell(commands):
    print("==> %s" % ' '.join(commands))
    subprocess.call(commands)


def cp(src, dest):
    shell(['cp', src, dest])


def zip(directory, zip_file):
    original_dir = os.getcwd()
    explicit_zip_path = os.path.join(original_dir, zip_file)
    os.chdir(directory)
    shell(['zip', '-r',  explicit_zip_path, '.', '-i', '*'])
    os.chdir(original_dir)


def py_files_in_directory(directory):
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for dirname in dirnames:
            if dirname.startswith("."):
                # Don't visit hidden directories
                dirnames.remove(dirname)
        for filename in filenames:
            # Don't mess with hidden files
            if filename.endswith(".py") and not filename.startswith("."):
                yield os.path.join(dirpath, filename)
