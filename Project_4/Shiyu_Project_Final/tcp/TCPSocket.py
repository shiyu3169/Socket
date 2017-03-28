#! /usr/bin/python3

import random
import datetime
import time
import fcntl
from IP.IPSocket import *
from tcp.TCPPacket import *
import threading


class TCPSocket:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.src = (get_ip(), random.randrange(0, 1 << 16))
        self.destination = None
        self.thread = None
        self.seq = 0
        self.received_packet = None
        self.ssthresh = float("inf")
        self.c_window = 1.0
        self.adv_window = float('inf')
        self.RTT = None
        self.MSS = 536
        self.next_packet = {
            'ack_num': 1,
            'seq': random.randrange(0, 1 << 32),
            'ack': 0
        }
        self.used_seqs = set()
        self.sending_packets = set()
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()
        self.resend_queue = queue.PriorityQueue()
        self.disorder_packets = queue.PriorityQueue()

    def connect(self, destination):
        """ Connect to server"""
        if self.thread is not None and self.thread.is_alive():
            # thread has been started
            return

        self.socket = IPSocket(get_ip())
        self.socket.connect(destination)
        self.destination = (socket.gethostbyname(destination[0]), destination[1])

        # handshake
        # starting seq number
        self.seq = random.randint(0, 65535)

        # Send the SYN packet
        syn_packet = TCPPacket(self.src, self.destination, 0, self.seq)
        syn_packet.syn = 1
        syn_packet.checksum()
        # Measure RTT
        sent_time = datetime.datetime.now()
        self.socket.send(syn_packet.build())
        now = time.time()
        packet = None
        # keep trying to receive SYN_ACK packets.
        while (time.time() - now) < 180 and packet is None:
            packet = self.socket.recv()
            if packet is not None:
                packet = TCPPacket.unpack(packet, self.destination[0], self.src[0])
                if packet.src == self.destination and packet.dest == self.src and packet.syn and packet.ack:
                    break
            time.sleep(0.01)
        else:
            raise Exception("No response from server for 3 minutes")

        # Calculate RTT
        arrive_time = datetime.datetime.now()
        self.RTT = (arrive_time - sent_time).total_seconds() * 1000

        # Get Advertised Window
        self.adv_window = packet.window

        # Get MSS
        for option in packet.options:
            if option['kind'] == 2 and option['length'] == 4:
                self.MSS = option['value']
                break

        # Get next seq
        self.next_packet['next_seq'] = packet.seq + len(packet.data) + 1
        self.seq = packet.ack_num

        # Send the ACK packet
        ack_packet = TCPPacket(self.src, self.destination, self.seq, self.next_packet['next_seq'])
        ack_packet.ack = 1
        ack_packet.checksum()
        self.socket.send(ack_packet.build())

        # start the thread
        self.connected = True
        self.thread = threading.Thread(name="tcp-running", target=self.tcp_running_thread)
        self.thread.setDaemon(True)
        self.thread.start()

    def tcp_running_thread(self):
        """
        running TCP threads
        """
        while True:
            if self.connected:
                self.send_packets()
                packet = self.socket.recv()

                while packet is not None:
                    self.convert_packet(packet)
                    packet = self.socket.recv()

                if not self.connected:
                    self.close()
                    break

                # check if timeout
                if self.RTT is not None:
                    t_packets = []
                    now = datetime.datetime.now()
                    for packet in self.sending_packets:
                        if (now - packet[1]).total_seconds() * 1000 > 2 * self.RTT:
                            t_packets.append(packet)

                    # update window if timeout
                    if len(t_packets) > 0:
                        self.ssthresh = self.c_window / 2
                        self.c_window = 1

                        # resend the timeout packets
                        for packet in t_packets:
                            self.sending_packets.remove(packet)
                            self.resend_queue.put((packet[0].seq, packet[0]))
                time.sleep(0.050)

    def send_packets(self):
        """Send or resend packets to server"""
        space = min(self.c_window, self.adv_window) / self.MSS - len(self.sending_packets)

        # resend the timeout packets
        while not self.resend_queue.empty():
            if space > 0:
                seq, packet = self.resend_queue.get()
                if len(packet) <= self.MSS:
                    self.socket.send(packet.build())
                    self.sending_packets.add((packet, datetime.datetime.now(), True))
            else:
                break

        # send new packets
        while not self.send_queue.empty():
            if space > 0:
                if not self.connected:
                    return
                else:
                    # Send a packet of data or ack another packet.
                    data = b''
                    while not self.send_queue.empty() and len(data) < self.MSS:
                        data += self.send_queue.get()

                    # Create packet
                    packet = TCPPacket(self.src, self.destination, self.seq, self.next_packet['next_seq'], data)
                    packet.ack = 1
                    packet.checksum()
                    # Track sending packet.
                    self.sending_packets.add((packet, datetime.datetime.now(), False))
                    # Send packet
                    self.socket.send(packet.build())
            else:
                break

    def convert_packet(self, packet):
        """Convert the packet"""
        packet = TCPPacket.unpack(packet, self.destination[0], self.src[0])
        packet.checksum()

        # Check validity
        if packet.check == 0 and packet.src == self.destination and packet.dest == self.src:
            # Get MSS
            for option in packet.options:
                if option['kind'] == 2 and option['length'] == 4:
                    self.MSS = option['value']
                    break

            if packet.fin or packet.rst:
                self.connected = False

            # Check if it contains data or syn
            if (len(packet.data) > 0) or packet.syn:
                self.next_packet['ack'] = 1

            # Deal ACK
            if packet.ack and packet.ack_num >= self.seq:
                self.ack_process(packet)

                # update the congestion window.
                if self.ssthresh <= self.c_window:
                    self.c_window += (1 / self.c_window)
                else:
                    self.c_window += 1

            # Get the next seq number
            next_seq = packet.seq + len(packet.data)
            if len(packet.data) > 0 and packet.seq == self.next_packet['next_seq']:
                # This is the packet we need.
                self.next_packet['next_seq'] = next_seq
                self.recv_queue.put(packet.data)
                while not self.disorder_packets.empty():
                    p = self.disorder_packets.get()
                    if p.seq == next_seq:
                        self.recv_queue.put(p.data)
                        next_seq = p.seq + len(p.data)
                    else:
                        self.disorder_packets.put(p)
                        break

            elif len(packet.data) > 0 and packet.seq > self.next_packet['next_seq'] and packet.seq not in self.used_seqs:
                # Packet is too early, store it.
                self.disorder_packets.put(packet)
                self.used_seqs.add(packet.seq)

            # Ack the packet if it has data
            if self.next_packet['ack']:
                p = TCPPacket(self.src, self.destination, self.seq, self.next_packet['next_seq'])
                p.ack = 1
                p.checksum()
                self.socket.send(p.build())

            self.adv_window = packet.window

    def ack_process(self, packet):
        """Deal the ACK packet"""
        self.seq = packet.ack_num

        # Find acked packets
        acked_p = set()
        packets_in_sending = self.sending_packets.copy()
        for packet in packets_in_sending:
            if self.next_packet['seq'] > packet[0].seq:
                self.sending_packets.remove(packet)
                acked_p.add(packet)

        # Manage RTT.
        now = datetime.datetime.now()
        alpha = 0.875

        for packet in acked_p:
            if not packet[2]:
                # Packet didn't time out so it's valid for RTT calculation
                rtt = now - packet[1]
                if self.RTT is not None:
                    self.RTT = alpha * self.RTT + (1 - alpha) * rtt.total_seconds() * 1000
                else:
                    self.RTT = rtt.total_seconds() * 1000

    def sendall(self, data):
        """Send all the data"""
        self.send_queue.put(data)

    def recv(self, maximum=None):
        """Get data from the socket"""
        if self.connected:
            packet = b''
            if self.received_packet is None:
                while not self.recv_queue.empty():
                    packet += self.recv_queue.get(block=False)
                if maximum is not None and len(packet) > maximum:
                    self.received_packet = packet[maximum:]
                    packet = packet[:maximum]
            else:
                packet = self.received_packet
                if maximum is None or len(packet) <= maximum:
                    self.received_packet = None
                else:
                    self.received_packet = packet[maximum:]
                    packet = packet[:maximum]
            return packet
        else:
            raise Exception("Socket closed")

    def close(self):
        """Close the socket"""
        self.next_packet['fin'] = 1
        p = TCPPacket(self.src, self.destination, 0, self.seq)
        p.fin = 1
        p.checksum()
        self.socket.send(p.build())
        self.connected = False

    def send(self, data):
        """Send some data over the network."""
        self.send_queue.put(data)


def get_ip(interface='eth0'):
    """Get ip address of the source, only works for linux machine"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = struct.pack('256s', interface[:15].encode())
    ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, data)[20:24])
    return ip
