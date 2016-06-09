import socket
import time
import sys
import ssl
import pprint
import struct
import random
import os
import threading
#v0.3
def versselect(con):
    if con==1:
        finalvers=int(ssl.PROTOCOL_SSLv23)
    elif con==2:
        finalvers=int(ssl.PROTOCOL_TLSv1)
    elif con==3:
        finalvers=int(ssl.PROTOCOL_SSLv3)
    else:
        print 'Incorrect index entered. Using default value'
        finalvers=int(ssl.PROTOCOL_SSLv23)
    return finalvers   
    

def sanitize(dirty):
    san_first=dirty.encode('hex')
    san_first=str(san_first)
    san_sec=san_first.replace('5c725c6e', '0d0a')
    san_third=san_sec.decode('hex')
    return san_third
    
#ssl23 sets record layer version to tlsv1 and clienthello to tlsv1.2 so max supports to 1.2
#TLSv1 sets record layer to v1 and clienthello to v1. v1 is the only version it supports
#sslv3 sets record and client hello to sslv3
#adding ssl2,tlsv1_1 or tlsv1_2 gives error

def ipstruct():
    global ips
    ips=['10.107.246.199']
    
    
def datastruct():
    global dictcol
    global num
    global garb
    global sslcheck
    global httpcheck
    
    a1='HTTP/1.1 302 Moved Temporarily\r\nLocation: http://10.105.5.75\r\nContent-Type: application/x-javascript\r\nlast-modified: Sat, 21 Dec 2013 23:06:35 GMT\r\ncache-control: max-age=604800\r\ndate: Tue, 16 Dec 2014 18:33:46 GMT\r\nconnection: Keep-Alive\r\n\r\n'
    a2= 'HTTP/1.1 200 OK\r\nContent-Type: application/x-javascript\r\nlast-modified: Sat, 21 Dec 2013 23:06:35 GMT\r\ncache-control: max-age=604800\r\ndate: Tue, 16 Dec 2014 18:33:46 GMT\r\nconnection: Keep-Alive\r\n\r\nContent-Length: 4\r\n\r\ntest'
    a3= int(ssl.PROTOCOL_SSLv23)
    a4= "HIGH:-aNULL:-eNULL"
    a5='This is udp server'
    a6='HTTP/1.1 302 Moved Temporarily\r\nLocation: http://10.105.5.75\r\nContent-Type: application/x-javascript\r\nlast-modified: Sat, 21 Dec 2013 23:06:35 GMT\r\ncache-control: max-age=604800\r\ndate: Tue, 16 Dec 2014 18:33:46 GMT\r\nconnection: Keep-Alive\r\n\r\n'
    ddict={'httpraw':a1, 'sslv':a3, 'sslcipher':a4,'udpraw':a5,'tcpraw':a6}

    if num==1:
        temph=raw_input('HTTP Menu\n1)Add http response raw\n2)Use default http response\n')
        temph=int(temph)
        if temph==1:
            temphhttp=raw_input('Enter http response raw\n')
            cleantemphhttp=sanitize(temphhttp)
            ddict['httpraw']=cleantemphhttp
            print ddict['httpraw']
        else:
            print ddict['httpraw']
            pass

        return ddict
    elif num==2:
        temps=raw_input('HTTP Menu\n1)Add http response raw\n2)Use default http response\n')
        temps=int(temps)
        if temps==1:
            tempshttp=raw_input('Enter http response raw\n')
            cleantempshttp=sanitize(tempshttp)
            ddict['httpraw']=cleantempshttp
            print ddict['httpraw']
        else:
            print ddict['httpraw']
            pass

        ss=raw_input('SSL Menu\n1)Enter ssl version\n2) Enter cipher string\n3)Manipulate both\n4)Go with default settings(cipher HIGH:-aNULL:-eNULL, sslv23)\n')
        ss=int(ss)
        if ss ==1:
            tempssl=raw_input('Enter index number\nAvailable for selection: 1)TLS1.2, 2)TLSv1, 3)SSLv3\n')
            tempssl=int(tempssl)
            tempsslv=versselect(tempssl)
            ddict['sslv']=tempsslv
            sslcheck=1
        elif ss==2:
            tempssl=raw_input('Enter cipher string\n')
            ddict['sslcipher']=tempssl
            sslcheck=2
        elif ss==3:
            tempssl=raw_input('Enter index number\nAvailable for selection: 1)TLS1.2, 2)TLSv1, 3)SSLv3\n')
            tempssl=int(tempssl)
            tempsslv=versselect(tempssl)
            ddict['sslv']=tempsslv
            tempsslc=raw_input('Enter cipher string\n')
            ddict['sslcipher']=tempsslc
            sslcheck=3
        else:
            pass

        return ddict
    elif garb==3:
        temph=raw_input('TCP Menu\n1)Add TCP response raw\n2)Use default TCP response\n')
        temph=int(temph)
        if temph==1:
            temphhttp=raw_input('Enter TCP response raw\n')
            cleantemphhttp=sanitize(temphhttp)
            ddict['tcpraw']=cleantemphhttp
            print ddict['tcpraw']
        else:
            print ddict['tcpraw']
            pass
        return ddict
    elif garb==4:
        temph=raw_input('UDP Menu\n1)Add UDP response raw\n2)Use default UDP response\n')
        temph=int(temph)
        if temph==1:
            temphhttp=raw_input('Enter UDP response raw\n')
            cleantemphhttp=sanitize(temphhttp)
            ddict['udpraw']=cleantemphhttp
            print ddict['udpraw']
        else:
            print ddict['udpraw']
            pass
        return ddict
def recv_timeout(the_socket,timeout):   

    the_socket.setblocking(0) 
     
 
    total_data=[]  
    data='' 
     
    
    begin=time.time() 
    while True:
        
        if total_data and time.time()-begin > timeout:  
            break
         

        elif time.time()-begin > timeout:  
            break 
         
        #recv something executed in try and expect 
        try:
            data = the_socket.recv(8192)
            if data:  
                total_data.append(data) 
               
                begin=time.time()  

        except:
            pass
     
    #join all parts to make final string
#    return ''.join(total_data)
    return total_data

def singserver():
    sr=raw_input('Would you like to use default ip settings?\nDefault settings:IP 10.107.246.199, gw 10.107.246.1. Enter y/n\n')
    if sr=='y':
        singserverip='10.107.246.199'
    else:
        
        ssip=raw_input('Enter server ip\n')
        ssmask=raw_input('Enter server ip netmask\n')
        print 'Configuring port eth1 with this IP configuration. Connect cable to this port please\n'
        cmd='ifconfig eth1 %s netmask %s'%(sr,smask)
        fp=os.popen(cmd)
        fp.close()
        while True:
            commands=raw_input('Enter routes desired for this interface. Example for single host- route add -host x.x.x.x gw y.y.y.y. For network route add -net x.x.x.x/24 gw y.y.y.y\nType done when finished adding routes\n')
            if commands=='done':
                break
            else:
                cmd==commands
                fp=os.popen(cmd)
                fp.close()

                
def multserver():
    ran=[]
    numsr=raw_input('Enter the number of servers\n')
    numsr=int(numsr)
    print 'Server IPs will need to be in the same subnet\n'
    multmask=raw_input('Enter subnet for this range of ips\n')
    
    z=0
    while z<numsr:
        firsts=raw_input('Enter ip address\n')
        ran.append(firsts)
        z=z+1
    popy=ran.pop(0)
    cmd='ifconfig eth1 %s netmask %s'%(popy,multmask)
    fp=os.popen(cmd)
    fp.close()
    subint=1
    subint=int(subint)
    for r in ran:
        cmd='ifconfig eth1:%d %s netmask %s'%(subint,r,multmask)
        fp=os.popen(cmd)
        fp.close()
        subint=subint+1
    print 'Server ips have been configured on port eth1. Please connect cable to eth1\n'
    while True:
            commands=raw_input('Enter desired route statements for this interface. Example for single host- route add -host x.x.x.x gw y.y.y.y. For network route add -net x.x.x.x/24 gw y.y.y.y\nType done when finished adding routes\n')
            if commands=='done':
                break
            else:
                cmd=commands
                fp=os.popen(cmd)
                fp.close()

def httptraffic(cl,p,tt,resp):
    global semaphore
    

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#    s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 20)
    try:
        s.bind((cl, p))  # ip and listening port for http
        s.listen(5)
        try:
            while True:
                semaphore.acquire()
                conn, addr = s.accept()

    #        print 'Connected by', addr
                recv_timeout(conn,tt)
                conn.sendall(resp)
                conn.close()
                semaphore.release
        except KeyboardInterrupt:
            print '\t\t\tctrl c sensed. Killing server threads....\n'

    except socket.error:
        print 'Socket already exists.Service already running on port %d.Check netstat on your machine.Skipping configuration of this service\n'%p
        sys.exit()

#def wrap_socket(sock, keyfile=None, certfile=None,
#                server_side=False, cert_reqs=CERT_NONE,
#                ssl_version=PROTOCOL_SSLv23, ca_certs=None,
#                do_handshake_on_connect=True):
def httpstraffic(cl,p,ttt,resps,ssv,ssc):
    global semaphore
 

    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        ss.bind((cl,p))
        ss.listen(5)
        try:
            while True:
                semaphore.acquire()
                conns, addrs = ss.accept()
                try:

                    ssl_sock=ssl.wrap_socket(conns,server_side=True,keyfile="server.key",certfile="server.crt",ciphers=ssc, ssl_version=ssv)
                    recv_timeout(ssl_sock,ttt)
                    ssl_sock.write(resps)
                    ssl_sock.close()
                    semaphore.release()
                except ssl.SSLError:
                    ssl_sock.close()
                    semaphore.release()
                    continue
        except KeyboardInterrupt:
            print '\t\t\tctrl c sensed. Killing server threads....\n'

    except socket.error:
        print 'Socket already exists.Service already running on port %d.Check netstat on your machine.Skipping configuration of this service\n'%p
        sys.exit()
def udptraffic(cl,p,tt,resp):
    global semaphore
 

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind((cl,p))
        try:
            while True:
                semaphore.acquire()
                data, addrs = s.recvfrom(4096)
                if data:
                    s.sendto(resp,addrs)
        except KeyboardInterrupt:
            semaphore.release()
            print '\t\t\tctrl c sensed. Killing server threads....\n'

            
    except socket.error:
        print 'Socket already exists.Service already running on port %d.Check netstat on your machine.Skipping configuration of this service\n'%p
        sys.exit()
# main loop
print'\t\t\t######beserve######\n'
print'\t\t\tserver emulator\n'
max_connections = 210 
global semaphore # protection againist overconsumption of host resources
semaphore = threading.BoundedSemaphore(max_connections)
global sslcheck
global httpcheck
global num
sslcheck=0
httpcheck=0
print 'IP Menu\n'
ipmenu=raw_input('1)Single server emulation\n2)Multiple server emulation. IP range-max 50 ips supported currently\n')
ipmenu=int(ipmenu)
if ipmenu==1:
    singserver()
elif ipmenu==2:
    multserver()
print 'Service Menu\n'    
num=raw_input('1)Http Server\n2)Https Server\n3)*Custom emulations*\n4)Multiservice emulation\nselect index\n')
num=int(num)
if num==1:
    sport=raw_input('Enter listening port for HTTP server\n')
    sport=int(sport)
    duration=raw_input('Enter response time for server\n')
    duration=float(duration)
    flavors=datastruct()
    content =flavors['httpraw']
    httptraffic('0.0.0.0',sport,duration,content)


elif num==2:
    ssport=raw_input('Enter listening port for HTTPs server\n')
    ssport=int(ssport)
    duration=raw_input('Enter response time for server\n')
    duration=float(duration)
    sslflavors=datastruct()
    content=sslflavors['httpraw']
    version=sslflavors['sslv']
    ciph=sslflavors['sslcipher']
    httpstraffic('0.0.0.0',ssport,duration,content,version,ciph)
elif num==4:
    print 'Multiservice Menu\n'
    global garb
    garb=raw_input('Add service\n1)HTTP\n2)HTTPS\n3)TCP Port\n4)UDP Port\n5)Done configuring\nEnter index to add service or 5 when you are done\n')
    garb=int(garb)
    while True:
        if garb==5:
            break
        elif garb==1:
            num=1
            sport=raw_input('Enter listening port for HTTP server\n')
            sport=int(sport)
            duration=raw_input('Enter response time for server\n')
            duration=float(duration)
            flavors=datastruct()
            content =flavors['httpraw']
            t = threading.Thread(target=httptraffic, args=('0.0.0.0',sport,duration,content))
            t.setDaemon(True)
            t.start()
            num=4
            garb=100
        elif garb==2:
            num=2
            ssport=raw_input('Enter listening port for HTTPs server\n')
            ssport=int(ssport)
            duration=raw_input('Enter response time for server\n')
            duration=float(duration)
            sslflavors=datastruct()
            content=sslflavors['httpraw']
            version=sslflavors['sslv']
            ciph=sslflavors['sslcipher']
            t = threading.Thread(target=httpstraffic, args=('0.0.0.0',ssport,duration,content,version,ciph))
            t.setDaemon(True)
            t.start()
            num=4
            garb=100
        elif garb==3:
            sport=raw_input('Enter listening port for TCP server\n')
            sport=int(sport)
            duration=raw_input('Enter response time for server\n')
            duration=float(duration)
            flavors=datastruct()
            content =flavors['tcpraw']
            t = threading.Thread(target=httptraffic, args=('0.0.0.0',sport,duration,content))  
            t.setDaemon(True)
            t.start()
            garb=100
        elif garb==4:
            sport=raw_input('Enter listening port for UDP server\n')
            sport=int(sport)
            duration=raw_input('Enter response time for server\n')
            duration=float(duration)
            flavors=datastruct()
            content =flavors['udpraw']
            t = threading.Thread(target=udptraffic, args=('0.0.0.0',sport,duration,content))  
            t.setDaemon(True)
            t.start()
            garb=100
        elif garb==100:
            garb=raw_input('Add service\n1)HTTP\n2)HTTPS\n3)TCP Port\n4)UDP Port\n5)Done configuring\nEnter index to add service or 5 when you are done\n')
            garb=int(garb)
        else:
            print'Please select valid index\n'
            break

            
finito=raw_input('Type any key and enter to shutdown servers and finish test\n')
if len(finito)>0:
    print '\t\t\tNote: beserve doesnt remove any network statements(IPs and routes) it configured\n'
    print '\t\t\tClosing all server threads and finishing test......'
    quit()

