from urequest import urlopen

f = urlopen("http://mirrors.mit.edu/ubuntu-releases/precise/ubuntu-12.04.5-server-amd64.iso.zsync")
print(f.read())
