#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Pyton interface to the simulated world. """

import argparse
import threading
import time
import os

import yaml
import zmq

from msg import sim_msgs_pb2
from msg import base_msgs_pb2
from msg import dev_msgs_pb2

class Control:
    """
    Simulator control API.

    Creates a command publisher and connects it to the simulator.

    :param string rtc_file_name: Name of the run-time configuraiton file. This file specifies the parameters for connecting to the simulator.

    """

    def __init__(self, rtc_file_name='', **kwargs):

        if rtc_file_name:
            # Parse the rtc file
            raise NotImplementedError(
                "RTC file parsing for Simulator control is not implemented yet. "
                "Please call the constructor with the name=beename argument.")
            pass
        else:
            # parse any keywords provided, otherwise take default values
            self.__pub_addr = kwargs.get('pub_addr', 'tcp://127.0.0.1:5556')
            self.__sub_addr = kwargs.get('sub_addr', 'tcp://127.0.0.1:5555')
            #self.__pub_addr = 'tcp://127.0.0.1:5556'
            self.__context = zmq.Context(1)
            self.__pub = self.__context.socket(zmq.PUB)
            self.__pub.connect(self.__pub_addr)
            # TODO: Fill readings with fake data
            #       to prevent program crashes.
            self.__absolute_time = base_msgs_pb2.Time()
            # Create the data update thread
            self.__connected = False
            self.__context = zmq.Context(1)
            self.__comm_thread = threading.Thread(target=self.__update_readings)
            self.__comm_thread.daemon = True
            self.__lock = threading.Lock()
            # Connect to the server and start receiving data
            self.__comm_thread.start()
            # Wait for the connection
            while not self.__connected:
                time.sleep(1)
            print('Simulator control connected!')

    def spawn(self,
              obj_type,
              name,
              pose,
              polygon = (),
              radius = (),
              color = (),
              height = 1,
              mass = -1):
        """

        Spawn an object in the simulated world.

        :param str obj_type: Type of object to spawn. Currently supported types are 'Casu', 'Bee', 'EPuck' and 'Physical'
        :param str name: Name of the object. Must be unique in the world.
        :param tuple pose: An (x,y,yaw) tuple.
        :param tuple polygon: A tuple of vertex coordinates ((x1,y1),(x2,y2),...). If obj_type is 'Physical', this defines the shape of the object.
        :param radius: Radius of a cylindrical 'Physical' object.
        :param color: Color of a 'Physical' object.
        :param float height: 'Physical' object height.
        :param mass: 'Physical' object mass.
        :return:  Nothing

        """
        data = sim_msgs_pb2.Spawn()
        data.pose.position.x = pose[0]
        data.pose.position.y = pose[1]
        data.pose.orientation.z = pose[2]
        data.type = obj_type
        data.name = name
        if len(color) == 3:
            data.color.red = color[0]
            data.color.green = color[1]
            data.color.blue = color[2]
        if (obj_type == 'Physical') and radius:
            data.cylinder.radius = radius
            data.cylinder.height = height
            data.cylinder.mass = mass
            data.type = 'Cylinder'
        if (obj_type == 'Physical') and polygon:
            for vertex in polygon:
                v = data.polygon.vertices.add()
                v.x = vertex[0]
                v.y = vertex[1]
            data.polygon.height = height
            data.polygon.mass = mass
            data.type = 'Polygon'
        self.__pub.send_multipart(['Sim', 'Spawn', obj_type,
                                   data.SerializeToString()])

    def spawn_array(self, obj_type, array):
        """
        Spawn an array of objects.
        """
        for name in array:
            self.spawn(obj_type, name,
                       (array[name]['pose']['x'],
                        array[name]['pose']['y'],
                        array[name]['pose']['yaw']))

    def teleport(self, obj_name, pose):
        """
        Teleport object to pose.
        """
        data = base_msgs_pb2.PoseStamped()
        data.pose.position.x = pose[0]
        data.pose.position.y = pose[1]
        data.pose.orientation.z = pose[2]
        self.__pub.send_multipart(['Sim', 'Teleport', obj_name,
                                   data.SerializeToString()])

    def reset_temperature (self, temp):
        """
        Reset world temperature to given value
        """
        temp_msg = dev_msgs_pb2.Temperature ()
        temp_msg.temp = temp
        self.__pub.send_multipart (['Sim', 'Heat', 'reset', temp_msg.SerializeToString ()])

    def kill(self, obj_name):
        """
        Kill an object in the simulated world.
        """
        pass

    def get_absolute_time(self):
        """
        Get the absolute time as reported by the assisi playground.

        :return: the absolute time as reported by the assisi playground.
        """
        with self.__lock:
            timestamp = self.__absolute_time.sec + self.__absolute_time.nsec*1e-9
        return timestamp

    def __update_readings(self):
        """
        Get data from assisi playground and update local data.
        """
        self.__sub = self.__context.socket(zmq.SUB)
        self.__sub.connect(self.__sub_addr)
        self.__sub.setsockopt(zmq.SUBSCRIBE, 'Sim')

        while True:
            [name, dev, cmd, data] = self.__sub.recv_multipart()
            self.__connected = True
            if dev == 'AbsoluteTime':
                if cmd == 'Value':
                    # Protect write with a lock
                    # to make sure all data is written before access
                    with self.__lock:
                        self.__absolute_time.ParseFromString(data)
                else:
                    print('Unknown command {0} for sim control'.format(cmd))


def spawn_array_from_file(array_filename):
    with open(array_filename) as array_file:
        arrays = yaml.safe_load(array_file)
        # Several arrays can be defined within one file
        for layer in arrays:
            # Spawn only simulated arrays
            if layer[:3].lower() == 'sim':
                print('Spawning objects in layer {0}...'.format(layer))
                if arrays[layer]:
                    # The array is non-empty, get the first element
                    obj_name = arrays[layer].keys()[0]
                    obj_type = obj_name.split('-')[0].title()
                    sim_ctrl = Control(pub_addr = arrays[layer][obj_name]['pub_addr'])
                    sim_ctrl.spawn_array(obj_type, arrays[layer])
    # no return value here

def main():
    parser = argparse.ArgumentParser(description='Spawn an array of objects (casus or bees), as defined in an .arena/.bees file.')
    parser.add_argument('specfile', help= 'name of file specifying the objects to spawn. Accepts: .arena or .bees direct spec, or .assisi project spec')
    args = parser.parse_args()

    # process specification to identify where definitions are
    if args.specfile.endswith(('.arena', '.bees')):
        spawn_array_from_file(args.specfile)
    elif args.specfile.endswith('.assisi'):
        # find any contained specification files (arena, agents)
        with open(args.specfile) as project_file:
            project = yaml.safe_load(project_file)

        project_root = os.path.dirname(os.path.abspath(args.specfile))
        found = 0
        keylist = ['arena', 'bees']
        for key in keylist:
            if key in project:
                found += 1
                array_filename = os.path.join(project_root, project[key])
                spawn_array_from_file(array_filename)

        if found == 0:
            raise IOError, "[E] specification file ({}) does not define any spawnable subfiles ({})\ndid you really supply an .assisi file?".format(", ".join(keylist),  args.specfile)
    else:
        # since we now accept multiple filetypes, it isn't obvious what to
        # assume except via extension. So halt here if does not conform
        raise IOError, "[E] specification file ({}) is of unknown type.\n             Accepted forms are .assisi, .arena, .bees".format(args.specfile)


if __name__ == '__main__':
    main()
