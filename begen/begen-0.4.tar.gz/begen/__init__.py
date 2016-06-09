import socket
import os
import time
import sys
import urllib
import ssl
import pprint
import struct
import random
import threading
#v0.4
def versselect(con):
    if con==1:
        finalvers=int(ssl.PROTOCOL_SSLv23)
    elif con==2:
        finalvers=int(ssl.PROTOCOL_TLSv1)
    elif con==3:
        finalvers=int(ssl.PROTOCOL_SSLv3)
    else:
        print 'Incorrect index entered. Using default value\n'
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

def datastruct():
    global dictcol
    global num
    global sslcheck
    global httpcheck
    
    a1='GET / HTTP/1.1\r\nHost: 10.105.5.75\r\nConnection: keep-alive\r\nUser-Agent: Jakarta Commons-HttpClient/3.0.1\r\n\r\n'
    a2= 'GET / HTTP/1.1\r\nHost: 10.105.5.75\r\nConnection: keep-alive\r\nUser-Agent: Jakarta Commons-HttpClient/3.0.1\r\nContent-Length: 4\r\n\r\ntest'
    a3= int(ssl.PROTOCOL_SSLv23)
    a4= "HIGH:-aNULL:-eNULL"
    ddict={'httpraw':a1, 'sslv':a3, 'sslcipher':a4}
    if num==1:
        temph=raw_input('HTTP Menu\n1)Add http request raw\n2)Use default http request\nselect index\n')
        temph=int(temph)
        if temph==1:
            temphhttp=raw_input('Enter http request raw\n')
            cleantemphhttp=sanitize(temphhttp)
            ddict['httpraw']=cleantemphhttp
            print ddict['httpraw']
        else:
            print ddict['httpraw']
            pass

        return ddict
    elif num==2:
        temps=raw_input('HTTP Menu\n1)Add http request raw\n2)Use default http request\nselect index\n')
        temps=int(temps)
        if temps==1:
            tempshttp=raw_input('Enter http request raw\n')
            cleantempshttp=sanitize(tempshttp)
            ddict['httpraw']=cleantempshttp
        else:
            pass

        ss=raw_input('SSL Menu\n1)Enter ssl version\n2) Enter cipher string\n3)Manipulate both\n4)Go with default settings(cipher HIGH:-aNULL:-eNULL and sslv23)\nselect index\n')
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
    else:
        pass
        
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

def httptraffic(bruce,cl,tt,req):
    global semaphore
    semaphore.acquire()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#    s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 20)
    s.bind((cl, 0))
    s.connect((bruce, 80))
    s.send(req)
    recv_timeout(s,tt)
    s.close()
    semaphore.release

#ssl.wrap_socket(sock,ciphers="HIGH:-aNULL:-eNULL:-PSK:RC4-SHA:RC4-MD5",ssl_version=ssl.PROTOCOL_TLSv1,cert_reqs=ssl.CERT_REQUIRED,ca_certs='/etc/ssl/certs/ca-bundle.crt')
# odd thing about ssl_version is its of type int
def httpstraffic(clark,cli,ttt,reqh,ssv,ssc):
    global semaphore
    semaphore.acquire()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((cli,0))
    ssl_sock=ssl.wrap_socket(s,ciphers=ssc, ssl_version=ssv)
    ssl_sock.connect((clark, 443))
    ssl_sock.write(reqh)
    recv_timeout(ssl_sock,ttt)
    ssl_sock.close()
    semaphore.release()

# main loop
print '\t\t\t######begen######\n'
print '\t\t\tTraffic Generator\n'
print '\t\t\t######v0.4######\n'
print '\t\t\t######arnabc######\n'

max_connections = 210 
global semaphore # protection againist overconsumption of host resources
semaphore = threading.BoundedSemaphore(max_connections)
global sslcheck
global httpcheck
global num
sslcheck=0
httpcheck=0
dst=raw_input('Enter target host\n')
sr=raw_input('Enter source host\n')
print 'Is this ip %s already configured on your network interface ?Answer y/n\n' %sr
ques=raw_input('')
if ques=='y':
    pass
else:
    print 'Would you like begen to configure the ip ?Answer y/n\n'
    ques2=raw_input('')
    if ques2=='n':
        pass
    else:
        newmask=raw_input('Enter mask for this IP\n')
        newint=raw_input('Enter interface name\n')
        newrout=raw_input('Enter route statement\n Example for a single host: route add -host x.x.x.x gw y.y.y.y. For network: route add -net x.x.x.x gw y.y.y.y\nPress enter to add no route\n')
        cmd='ifconfig %s %s netmask %s'%(newint,sr,newmask)
        fp=os.popen(cmd)
        fp.close()
        if len(newrout)>1:
            cmd=newrout
            fp=os.popen(cmd)
            fp.close()
        else:
            pass
num=raw_input('Menu\n1)Http traffic\n2)Https traffic\n3)*Custom emulations*\nselect index\n')
num=int(num)
goal=raw_input('Enter  goal for traffic\n1)concurrent connections\n2)CPS\nselect index\n' )
goal=int(goal)
if goal==1:
    simu=raw_input('Enter number of concurrent connections\n')
    simu=int(simu)
    duration=raw_input('Enter total test duration\n')
    duration= float(duration)
    if num==1:
        flavors=datastruct()
        content =flavors['httpraw']
        for i in xrange(simu):
            t = threading.Thread(target=httptraffic, args=(dst,sr,duration,content))  
            t.start()

    elif num==2:
        sslflavors=datastruct()
        content=sslflavors['httpraw']
        version=sslflavors['sslv']
        ciph=sslflavors['sslcipher']
        for i in xrange(simu):
            t = threading.Thread(target=httpstraffic, args=(dst,sr,duration,content, version, ciph))
            t.start()
            
else:
    cps=raw_input('Enter CPS desired\n')
    cps=int(cps)
    tot=raw_input('Enter total connections\n')
    tot=int(tot)
    duration=raw_input('Specify how long will client wait for a response(secs)\n')
    duration=float(duration)
    if num==1:
        flavors=datastruct()
        content =flavors['httpraw']
        control=0
        fact=1
        for i in xrange(tot):
            t = threading.Thread(target=httptraffic, args=(dst,sr,duration,content))  
            t.start()
            control=control +1
            if control==(fact*cps):
                time.sleep(0.8)
                fact=fact+1
            else:
                pass

    elif num==2:
        sslflavors=datastruct()
        content=sslflavors['httpraw']
        version=sslflavors['sslv']
        ciph=sslflavors['sslcipher']
        control=0
        fact=1
        for i in xrange(tot):
            t = threading.Thread(target=httpstraffic, args=(dst,sr,duration,content, version, ciph))
            t.start()
            control=control +1
            if control==(fact*cps):
                time.sleep(0.8)
                fact=fact+1
            else:
                pass
    

t.join() # to check if all threads have closed successfully
print '\t\t\tAll client threads have exited'
print '\t\t\tNote: begen doesnt remove any network statements(IPs and routes) it configured\n'
print '\t\t\tTest has finished\n'

