import socket
import struct
import hashlib
import random

from moneywagon.crypto_data import crypto_data

def netaddr(ipaddr, port):
    services = 1
    s1 = struct.pack('<Q12s', services, '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff')
    s2 = struct.pack('>4sH', ipaddr, port)
    return s1 + s2

def makeMessage(magic, command, payload):
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[0:4]
    return struct.pack('L12sL4s', magic, command, len(payload), checksum) + payload

def getVersionMsg(magic):
    version = 60002
    services = 1
    timestamp = int(time.time())
    addr_me = utils.netaddr(socket.inet_aton("127.0.0.1"), 8333)
    addr_you = utils.netaddr(socket.inet_aton("127.0.0.1"), 8333)
    nonce = random.getrandbits(64)
    sub_version_num = utils.varstr('')
    start_height = 0

    payload = struct.pack(
        '<LQQ26s26sQsL', version, services, timestamp, addr_me,
        addr_you, nonce, sub_version_num, start_height
    )
    return makeMessage(magic, 'version', payload)

def getTxMsg(magic, payload):
  return makeMessage(magic, 'tx', payload)

def raw_pushtx(tx, currency):
    magic = crypto_data[currency]['message_magic']
    peer = random.choice(crypto_data[currency]['peer_seeds'])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((peer, 8333))

    sock.send(getVersionMsg(magic))
    sock.recv(1000) # receive version
    sock.recv(1000) # receive verack
    sock.send(getTxMsg(magic, tx.decode('hex')))
