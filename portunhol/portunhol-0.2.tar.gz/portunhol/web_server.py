from portunhol import main as translate
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

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    line = cl.read()
    print(line)
    translated = translate(line)
    response = html % (line, translated)
    cl.send(response)
    cl.close()