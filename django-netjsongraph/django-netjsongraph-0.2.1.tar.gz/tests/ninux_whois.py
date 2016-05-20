import socket
import requests

from django.db.models.signals import pre_save
from django.dispatch import receiver

from django_netjsongraph.models import Node


def whois(query, hostname='chi.ninux.org'):
    """
    Retrieve node information from Ninux.org WHOIS service
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, 43))
    s.send('{0}\r\n'.format(query).encode('utf8'))
    response = ''
    while True:
        d = s.recv(4096)
        response += d.decode('utf8')
        if not d:
            break
    s.close()
    fields = {}
    for line in response.split('\n'):
        if ':' not in line or line.startswith('%'):
            continue
        parts = line.split(':  ')
        key = parts[0].strip()
        value = ''.join(parts[1:]).strip()
        if value in ['-', 'xxx', '', '--', '---']:
            continue
        fields[key] = value
    return fields


def nodeshot_api(address):
    uri = 'https://ninux.nodeshot.org/api/v1/whois/%s/?format=json' % address
    try:
        response = requests.get(uri)
    except Exception:
        return None
    else:
        return response.json().get('node')


@receiver(pre_save, sender=Node, dispatch_uid='resolve_node')
def resolve_node(sender, instance, **kwargs):
    whois_fields = whois(instance.netjson_id)
    whois_fields['nodeshot'] = nodeshot_api(instance.netjson_id)
    # determine label
    label_keys = ['nodeshot',
                  'node',
                  'posizione-zona',
                  'map-server',
                  'name']
    for key in label_keys:
        label = whois_fields.get(key)
        if label:
            instance.label = label
            break
    # store interesting properties for visualization purposes
    interesting_keys = ['posizione-zona',
                        'technical-contact',
                        'name',
                        'essid',
                        'apparato']
    for key in interesting_keys:
        if key in whois_fields:
            instance.properties[key] = whois_fields[key]
