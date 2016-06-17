from iofunc import *

# Reading
file = open("iofunc.py", "r")
print(file_readline(file))
file_close(file)

# Writing
file = open("test.txt", "w")
file_write(file, "Hello World!")
file_close(file)

