#!/bin/python
import click
from libcloud.compute.drivers.dimensiondata import DimensionDataNodeDriver
import json
from requests import HTTPError
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

try:
    import configparser
except ImportError:
    import ConfigParser as configparser
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

@click.command()
@click.option('--masterdc', type=click.UNPROCESSED, required=True, help='The master datacenter to compare')
@click.option('--drdc', type=click.UNPROCESSED, required=True, help='The DR datacenter')
@click.option('--user', prompt='username', help='username')
@click.option('--password', prompt='password', hide_input=True, help='password')
@click.option('--verbose', is_flag=True, default=False, help='Verbosity')
def compare(masterdc, drdc, user, password, verbose):
    client = DimensionDataNodeDriver(user, password)
    master_nodes = client.list_nodes(ex_location=masterdc)
    dr_nodes = client.list_nodes(ex_location=drdc)

    master_node_dict = convert_nodes(master_nodes)
    dr_node_dict = convert_nodes(dr_nodes)

    compare_nodes(master_node_dict, dr_node_dict, verbose)

def compare_nodes(master, dr, verbose=False):
    for key in master.keys():
        ip_split = key.split('.')
        ip_split[2] = str(int(ip_split[2]) + 16)
        dr_key = '.'.join(ip_split)
        #click.secho("Attempting to find a DR match for {}".format(key))
        if dr.has_key(dr_key):
            print("Found a match Master: {} DR: {}".format(key, dr_key))
            if node_specs_match(master[key], dr[dr_key], verbose):
                click.secho("Node matches", fg='green')
            else:
                click.secho("Node {} with ip {} does not match {} with ip {}".format(master[key]['name'], key, dr[dr_key]['name'], key), fg='red')

            click.secho("")
        else:
            #print("No DR Server {}".format(dr_key))
            pass

def node_specs_match(n1, n2, verbose=False):
    click.secho("Comparing node {} and {}".format(n1['name'], n2['name']))
    match = True
    for key in n1.keys():
        if key is 'name':
            continue
        if n1[key] != n2[key]:
            match = False
            click.secho("{} does not match {} vs {}".format(key, n1[key], n2[key]), fg='red')
        elif verbose:
            click.secho("{} matches for node".format(key), fg='green')
    return match

def convert_nodes(node_list):
    node_dict = {}
    for node in node_list:
        node_dict[node.private_ips[0]] = {'cpu_count': node.extra['cpu'].cpu_count,
                                          'cpu_performance': node.extra['cpu'].performance,
                                          'cpu_cores_per_socket': node.extra['cpu'].cores_per_socket,
                                          'os_name': node.extra['OS_displayName'],
                                          'os_type': node.extra['OS_type'],
                                          'disks': convert_disks(node.extra['disks']),
                                          'memory': node.extra['memoryMb'],
                                          'name': node.name
                                         }
    return node_dict

def convert_disks(disks):
    disk_dict = {}
    for disk in disks:
        disk_dict[disk.scsi_id] = {
            'size_gb': disk.size_gb,
            'speed': disk.speed
        }

    return disk_dict


if __name__ == '__main__':
    compare()
