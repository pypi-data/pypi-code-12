import os
os.chdir('/tmp/HeadFirstPython/chapter3')
try:
    data = open('sketch.txt')

    for each_line in data:
        try:
        #if each_line.find(':') > 0:
                (role, line_spoken) = each_line.split(':',1)
                print(role, end='')
                print(' said:', end='')
                print(line_spoken, end='')
        except ValueError:
            pass

    data.close()

except IOError:
    print("The file is missing")

