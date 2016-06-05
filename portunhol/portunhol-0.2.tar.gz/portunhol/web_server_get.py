from portunhol import para_el_portunhol
html = """
<!DOCTYPE html>
<html>
    <head> <title>Portunhol</title> </head>
    <body>
        <h1>Portugues:</h1>
        <p>%s</p>

        <h1>Portunhol:</h1>
        <p>%s</p>
    </body>
</html>
"""

import socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)
word = ''
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        read_word = False
        while True:
            line = cl_file.readline()
            line_str = str(line)
            if not read_word and line_str.upper().find('GET'):
                word = line_str.split('portunhol?palabra=')[1].split(' ')[0]
                read_word = True
            if not line or line == b'\r\n':
                break
        translated = para_el_portunhol(word.lower())
        response = html % (word, translated)
        cl.send(response)
        cl.close()
    except:
        cl.close()
