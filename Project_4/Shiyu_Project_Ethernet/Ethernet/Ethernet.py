#! /usr/bin/python3

import binascii
import socket
import struct
import sys

from utility import get_mac_address, get_gateway_ip, get_localhost_ip

ARPOP_REQUEST = 1
ARPOP_REPLY = 2


class EthernetPacket:
    def __init__(self, src='0', dst='0', proto=0x800, data=''):
        self.dst = dst
        self.src = src
        self.type = proto
        self.data = data

    def build(self):
        """
        Build the ethernet frame in binary format
        :return:
        """
        frame = struct.pack('!6s6sH',
                            binascii.unhexlify(self.dst),
                            binascii.unhexlify(self.src),
                            self.type) + self.data

        return frame

    def rebuild(self, raw_packet):
        """
        Rebuild the ethernet frame
        :param raw_packet:
        """
        [dst, src, self.type] = struct.unpack('!6s6sH', raw_packet[:14])
        self.data = raw_packet[14:]
        self.src = binascii.hexlify(src)
        self.dst = binascii.hexlify(dst)

    def debug_print(self):
        """
        Print information about the object of EthernetPacket for debugging
        """
        print('[DEBUG]Ethernet Packet')
        print("From: %s\tTo: %s\tType: %X" % (self.src, self.dst, self.type))


class ARPPacket:
    def __init__(self):
        self.htype = 0x0001  # ethernet
        self.ptype = 0x0800  # ip arp resolution
        self.hlen = 6  # len(Mac Address)
        self.plen = 4  # len(IP Address)
        self.op = 1  # 1 for request, 2 for reply
        self.src_mac = ''
        self.src_ip = ''
        self.dst_mac = ''
        self.dst_ip = ''

    def build(self):
        frame = struct.pack('!HHBBH6s4s6s4s',
                            self.htype,
                            self.ptype,
                            self.hlen,
                            self.plen,
                            self.op,
                            binascii.unhexlify(self.src_mac),
                            socket.inet_aton(self.src_ip),
                            binascii.unhexlify(self.dst_mac),
                            socket.inet_aton(self.dst_ip))
        return frame

    def rebuild(self, raw_packet):
        [self.htype,
         self.ptype,
         self.hlen,
         self.plen,
         self.op,
         src_mac,
         src_ip,
         dst_mac,
         dst_ip] = struct.unpack('!HHBBH6s4s6s4s', raw_packet)

        self.src_mac = binascii.hexlify(src_mac)
        self.src_ip = socket.inet_ntoa(src_ip)

        self.dst_mac = binascii.hexlify(dst_mac)
        self.dst_ip = socket.inet_ntoa(dst_ip)

    def debug_print(self):
        if self.op == ARPOP_REQUEST:
            print('[DEBUG]ARP Request:')
            print('%s @ %s request %s' % (self.src_mac, self.src_ip, self.dst_ip))
        if self.op == ARPOP_REPLY:
            print('[DEBUG]ARP Reply:')
            print('%s @ %s' % (self.src_mac, self.src_ip))


class EthernetSocket:
    def __init__(self):
        self.src_mac = ''
        self.dst_mac = ''
        self.gateway_mac = ''  # Mac address of the default gateway

        self.send_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        self.send_sock.bind(('eth0', 0))

        self.recv_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
        self.recv_sock.setblocking(0)

    def send(self, data):
        if self.gateway_mac == '':
            gateway_ip = get_gateway_ip()
            try:
                self.gateway_mac = self.find_mac(gateway_ip)
            except:
                print('cannot get getway')
                sys.exit('ARP Request ' + gateway_ip + ' is Failed')

        self.dst_mac = self.gateway_mac
        packet = EthernetPacket(self.src_mac, self.dst_mac, data=data)

        # print '[DEBUG]Send Ethernet Packet'
        # packet.debug_print()
        self.send_sock.send(packet.build())

    def recv(self):
        packet = EthernetPacket()
        while True:
            pkt = self.recv_sock.recv(4096)
            packet.rebuild(pkt)
            if packet.dst.decode("utf-8") == self.src_mac:  # and packet.src_mac == self.dst_mac:
                return packet.data

    def find_mac(self, dst_ip):

        send_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        recv_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0806))
        recv_sock.settimeout(1)

        self.src_mac = get_mac_address('eth0')
        src_ip = get_localhost_ip()

        arp_req = ARPPacket()
        arp_req.src_mac = self.src_mac
        arp_req.src_ip = src_ip
        arp_req.dst_mac = '000000000000'
        arp_req.dst_ip = dst_ip
        arp_req.op = ARPOP_REQUEST

        packet = EthernetPacket(self.src_mac, 'ffffffffffff', 0x0806, arp_req.build())
        # print('[DEBUG]Send Ethernet packet')
        # packet.debug_print()
        send_sock.sendto(packet.build(), ('eth0', 0))

        arp_res = ARPPacket()
        while True:
            pkt = recv_sock.recv(4096)
            packet.rebuild(pkt)

            if packet.dst.decode("utf-8") == self.src_mac:
                # print('[DEBUG]ARP REPLY Ethernet Packet')
                # packet.debug_print()
                arp_res.rebuild(packet.data[:28])
                # arp_res.debug_print()
                if arp_res.src_ip == dst_ip and arp_res.dst_ip == src_ip:
                    break

        send_sock.close()
        recv_sock.close()
        return arp_res.src_mac


if __name__ == '__main__':
    s = EthernetSocket()
    s.find_mac(get_gateway_ip())