""" 
Python API for manipulating simulated physical objects. 
"""

import threading
import time

import zmq

from msg import base_msgs_pb2

class Object:
    """ 
    Interface to simulated physical objects. 

    Connects to the simulated physical object. 

    :param string rtc_file_name: Name of the RTC file.
    :param string name: Unique name of the spawned physical object.

    """
    
    def __init__(self, rtc_file_name='', name = 'object'):

        
        if rtc_file_name:
            # Parse the rtc file
            pass
        else:
            # Use default values
            self.__pub_addr = 'tcp://127.0.0.1:5556'
            self.__sub_addr = 'tcp://127.0.0.1:5555',
            self.__name = name
            self.x = 0
            self.y = 0
            self.yaw = 0

            # Create the data update thread
            self.__connected = False
            self.__context = zmq.Context(1)
            self.__comm_thread = threading.Thread(target=self.__update_readings)
            self.__comm_thread.daemon = True
            self.__lock = threading.Lock()
            self.__comm_thread.start()

            # Bind the publisher socket
            self.__pub = self.__context.socket(zmq.PUB)
            self.__pub.connect(self.__pub_addr)

            # Wait for the connection
            while not self.__connected:
                pass
            print('{0} connected!'.format(self.__name))

            # Wait one more second to get all the data
            time.sleep(1)

    def __update_readings(self):
        """  
        Get message from object and update data. 
        """
        self.__sub = self.__context.socket(zmq.SUB)
        self.__sub.connect(self.__sub_addr)
        self.__sub.setsockopt(zmq.SUBSCRIBE, self.__name)
        
        while True:
            [name, dev, cmd, data] = self.__sub.recv_multipart()
            self.__connected = True
            if dev == 'Pos':
                if cmd == 'Get':
                    # Protect write with a lock
                    # to make sure all data is written before access
                    pose = base_msgs_pb2.PoseStamped()
                    with self.__lock:
                        pose.ParseFromString(data)
                    self.x = pose.pose.position.x
                    self.y = pose.pose.position.y
                    self.yaw = pose.pose.orientation.z
                else:
                    print('Unknown command {0} from {1}'.format(ranges, self.__name))
            else:
                print('Unknown device ir for {0}'.format(self.__name))

if __name__ == '__main__':
    
    pass
