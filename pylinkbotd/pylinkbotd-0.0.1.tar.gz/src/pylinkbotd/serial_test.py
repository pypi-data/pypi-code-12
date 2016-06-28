import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
ps = []
for p in ports:
    print(p[1])
    ps.append(p)

print(ps[0] == ps[1])

ports = serial.tools.list_ports.comports()
pss = []
for p in ports:
    print(p[1])
    pss.append(p)

print(ps[0] == pss[0])
