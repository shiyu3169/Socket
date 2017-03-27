#! /usr/bin/python3

import subprocess
import fcntl
import socket
import struct


class ChecksumError(Exception):
    def __init__(self, _type):
        self.type = _type

    def __str__(self):
        return self.type + ' checksum is not match.'


class TimeOutError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return 'Timeout Error'


def get_open_port():
    """Get a free port for TCP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def get_mac_address(iface='eth0'):
    """Return the MAC address of the localhost
    :param iface: 
    """
    mac = subprocess.getoutput("ifconfig " + iface + " | grep HWaddr | awk '{ print $5 }'")
    if len(mac) == 17:
        return mac.replace(':', '')


def get_localhost_ip(iface='eth0'):
    """Return the IP address of localhost
    :param iface:
    """
    """Get ip address of the source, only works for linux machine"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = struct.pack('256s', iface[:15].encode())
    ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, data)[20:24])
    return ip


def get_gateway_ip():
    """Return the IP address of the default gateway."""
    gateway_ip = ''
    data = subprocess.getoutput('route -n').split('\n')
    for line in data:
        record = line.split()
        if record[0] == '0.0.0.0':
            gateway_ip = record[1]
            break
    return gateway_ip


def checksum(msg):
    """checksum functions needed for calculation checksum
    :param msg: 
    """
    if len(msg) % 2 == 1:  # the length of msg in bytes is an odd number
        msg += struct.pack('B', 0)
    s = 0
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s += w
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    # complement and mask to 4 byte short
    s = ~s & 0xffff
    return s


if __name__ == "__main__":
    print('MAC Address: ' + get_mac_address())
    print('IP Address: ' + get_localhost_ip())
    print('Default Gateway IP Address: ' + get_gateway_ip())