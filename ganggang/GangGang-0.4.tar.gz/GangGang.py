import socket
import pickle
import sys
import time

def recv_timeout( the_socket , timeout=1): # implements recvall, from http://www.binarytides.com/receive-full-data-with-the-recv-socket-function-in-python/
    the_socket.setblocking(0)
    total_data=[]
    data=''
    begin = time.time()
    while True:
        #if you got some data, then break after timeout
        if total_data and time.time() - begin > timeout:
            break
        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time() - begin > timeout * 2:
            break
        #recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                #change the beginning time for measurement
                begin=time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
    #join all parts to make final string
    return ''.join(total_data)

def recieve_and_unpickle( socket):
    rawdata = recv_timeout(socket)
    if len(rawdata) > 0:
        try:
            return pickle.loads(rawdata)
        except EOFError, e:
            return None

def process_data(data, socket, custom_function):
    if type(data).__name__ != 'list':
        raise TypeError('data is not a list!') 
    result = custom_function(data)
    return result

def return_data(result, socket):
    pickle_result = pickle.dumps(result, 0)
    socket.sendall(str(pickle_result))

def server(host, port, custom_function):
    # listen and execute
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind((host, port))
    serversocket.listen(5) # become a server socket, maximum 5 connections

    while True:
        try:
            conn, addr = serversocket.accept()
            data = recieve_and_unpickle(conn)
            result = process_data(data, conn, custom_function)
            return_data(result, conn)
        except Exception, e:
            print e
            break;
    serversocket.close()

def client(host, port, data):
    # send and recieve
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientsocket.connect((host, port))
    except Exception, e:
        print e
        
    pickle_data = pickle.dumps(data, 0)
    clientsocket.send(pickle_data)
    # synchronous
    recv_data = recieve_and_unpickle(clientsocket)
    clientsocket.close()
    return recv_data


