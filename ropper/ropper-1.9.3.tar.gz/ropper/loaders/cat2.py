import png

r = png.Reader('test2.png')

s = ''
for c in r.chunks():
    if c[0] == 'IDAT':
        s += c[1]

s = s.encode('zlib')

b = 0
count = 0
for c in s:
    b <<= 1
    b = ord(c) & 1
    count += 1

    if count == 8:
        print chr(b),
        b = 0