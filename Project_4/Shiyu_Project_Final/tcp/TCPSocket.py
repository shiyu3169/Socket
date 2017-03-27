import random
import datetime
import time
import fcntl
from IP.IPSocket import *
from tcp.TCPPacket import *
import threading


def get_ip(ifname='eth0'):
    """
    Get ip address of the source, only works for linux machine
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = struct.pack('256s', ifname[:15].encode())
    ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, data)[20:24])
    return ip


class TCPSocket:
    """
    A TCP socket which is functions like normal socket
    """
    def __init__(self):
        self.socket = None
        self.src = (get_ip(), random.randrange(0, 1 << 16))
        self.dest = None
        self.thread = None
        self.seq = 0
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()
        self.connected = False
        self.received_packet = None
        self.ssthresh = float("inf")
        self.congestion_window = 1
        self.dest_window = float('inf')
        self.RTT = None
        self.MSS = 536
        self.next_packet = {
            'ack_num': 1,
            'seq': random.randrange(0, 1 << 32),
            'ack': 0
        }
        # collection of packets that are currently in the network,
        # the set has three elements, packet, start time and a boolean to show it is being resent
        self.sending_packets = set()
        self.resend_queue = queue.PriorityQueue()
        self.disorder_packets = queue.PriorityQueue()
        self.seen_seq_nums = set()

    def connect(self, dest):
        """
        Create a new connection
        """
        if self.thread is not None and self.thread.is_alive():
            # Already connected
            return

        self.socket = IPSocket(get_ip())
        self.socket.connect(dest)
        self.dest = (socket.gethostbyname(dest[0]), dest[1])

        # start the thread
        self.handshake()
        self.thread = threading.Thread(name="tcp-loop", target=self.loop)
        self.thread.setDaemon(True)
        self.thread.start()

    def send(self, data):
        """
        Send some data over the network.
        """
        self.send_queue.put(data)

    def sendall(self, data):
        """
        Send all the data over the socket.
        """
        self.send_queue.put(data)


    def recv(self, max_bytes=None):
        """
        Get data from the socket
        """
        packet = b''
        if not self.connected:
            raise Exception("Socket closed")

        if self.received_packet is None:
            while True:
                if not self.connected:
                    raise Exception("Socket closed")
                if not self.recv_queue.empty():
                    packet += self.recv_queue.get(block=False)
                else:
                    break
            if max_bytes is not None and len(packet) > max_bytes:
                self.received_packet = packet[max_bytes:]
                packet = packet[:max_bytes]
        else:
            packet = self.received_packet
            if max_bytes is None or len(packet) <= max_bytes:
                self.received_packet = None
            else:
                self.received_packet = packet[max_bytes:]
                packet = packet[:max_bytes]

        return packet


    def close(self):
        """
        Close the socket
        """
        self.next_packet['fin'] = 1
        p = TCPPacket(self.src, self.dest, 0, self.seq)
        p.fin = 1
        p.checksum()
        self.socket.send(p.build())
        self.connected = False

    def loop(self):
        """
        Thread target for running TCP separate from application.
        """
        while True:
            if self.connected:
                self.send_packets()
                packet = self.socket.recv()
                while packet is not None:
                    self.parse_packet(packet)
                    packet = self.socket.recv()

                if not self.connected:
                    self.close()
                    break

                if self.RTT is not None:
                    self.check_time()

                # Gotta avoid busy wait
                time.sleep(0.050)

    def handshake(self):
        """
        Perform the three-way handshake.
        """

        # Choose the starting seq number
        self.seq = random.randint(0, 65535)

        # Send the SYN packet to create the connection
        syn = TCPPacket(self.src, self.dest, 0, self.seq)
        syn.syn = 1
        syn.checksum()

        sent_time = datetime.datetime.now()
        self.socket.send(syn.build())

        # Get packets until we see a SYN_ACK from the destination to us.
        while True:
            p = self.socket.recv()
            if p is not None:
                p = TCPPacket.unpack(p, self.dest[0], self.src[0])
                if p.src == self.dest and p.dest == self.src and p.syn and p.ack:
                    break
            time.sleep(0.01)

        # Calculate Initial RTT
        arrive_time = datetime.datetime.now()
        self.RTT = (arrive_time - sent_time).total_seconds() * 1000

        # Get Advertised Window Info
        self.dest_window = p.window

        # Pull out MSS Information
        for o in p.options:
            if o['kind'] == 2 and o['length'] == 4:
                self.MSS = o['value']
                break

        # Calculate next seq numbers to see.
        self.next_packet['next_expected_seq'] = p.seq + len(p.data) + 1
        self.seq = p.ack_num

        # Send the ACK packet to open the connection of both sides.
        ack = TCPPacket(self.src, self.dest, self.seq, self.next_packet['next_expected_seq'])
        ack.ack = 1
        ack.checksum()
        self.socket.send(ack.build())

        self.connected = True

    def parse_packet(self, packet):
        """
        Convert the packet to an object.
        Filter packets that aren't part of this connection.
        Store data and ACK appropriately.
        :param packet: A byte string containing a tcp packet.
        """
        packet = TCPPacket.unpack(packet, self.dest[0], self.src[0])
        packet.checksum()
        # Check validity
        if packet.check == 0 and packet.src == self.dest and packet.dest == self.src:

            # Pull out MSS Information
            for o in packet.options:
                if o['kind'] == 2 and o['length'] == 4:
                    self.MSS = o['value']
                    break

            # Handle ACK
            if packet.ack and packet.ack_num >= self.seq:
                self.handle_ack(packet)

            # Check if it contains data or FIN or SYN
            if (len(packet.data) > 0) or packet.syn:
                self.next_packet['ack'] = 1

            # Update the next expected seq number
            next_seq = packet.seq + len(packet.data)
            if len(packet.data) > 0 and packet.seq == self.next_packet['next_expected_seq']:
                # This is the packet we need.
                self.next_packet['next_expected_seq'] = next_seq
                self.recv_queue.put(packet.data)
                while not self.disorder_packets.empty():
                    p = self.disorder_packets.get()
                    if p.seq == next_seq:
                        self.recv_queue.put(p.data)
                        next_seq = p.seq + len(p.data)
                    else:
                        self.disorder_packets.put(p)
                        break
            elif len(packet.data) > 0 and packet.seq > self.next_packet[
                'next_expected_seq'] and packet.seq not in self.seen_seq_nums:
                # Packet is too early, store it.
                self.disorder_packets.put(packet)
                self.seen_seq_nums.add(packet.seq)

            # Ack the packet if it has data
            if self.next_packet['ack']:
                p = TCPPacket(self.src, self.dest, self.seq, self.next_packet['next_expected_seq'])
                p.ack = 1
                p.checksum()
                self.socket.send(p.build())

            self.dest_window = packet.window

            if packet.fin or packet.rst:
                self.connected = False

    def handle_ack(self, packet):
        """
        Handles the ACK clocking part of TCP.
        """
        # Increase the congestion window.
        if self.ssthresh <= self.congestion_window:
            self.congestion_window += (1 / self.congestion_window)
        else:
            self.congestion_window += 1

        self.seq = packet.ack_num

        # Find acked packets
        acked_packets = set()
        packets_in_sending = self.sending_packets.copy()
        for p in packets_in_sending:
            if p[0].seq <= self.next_packet['seq']:
                acked_packets.add(p)
                self.sending_packets.remove(p)

        # Manage RTT.
        now = datetime.datetime.now()
        ALPHA = 0.875  # NEW_RTT = ALPHA * OLD_RTT + (1 - ALPHA) * PACKET_RTT

        for p in acked_packets:
            if not p[2]:
                # Packet didn't time out so it's valid for RTT calculation
                packet_rtt = now - p[1]
                if self.RTT is not None:
                    self.RTT = ALPHA * self.RTT + (1 - ALPHA) * packet_rtt.total_seconds() * 1000
                else:
                    self.RTT = packet_rtt.total_seconds() * 1000


    def check_time(self):
        """
        Check to see if any previously sent packets have timed out while waiting to be
        ACKed
        """
        timeout_packets = []
        now = datetime.datetime.now()
        for p in self.sending_packets:
            t = (now - p[1]).total_seconds() * 1000
            if t > 2 * self.RTT:
                timeout_packets.append(p)

        if len(timeout_packets) > 0:
            self.ssthresh = self.congestion_window / 2
            self.congestion_window = 1

            for p in timeout_packets:
                self.sending_packets.remove(p)
                self.resend_queue.put((p[0].seq, p[0]))

    def send_packets(self):
        """
        Send new packets containing the data passed into the socket via send,
        and resend timed out packets. Do so until the window if full.
        """
        space = min(self.congestion_window, self.dest_window) / self.MSS - len(self.sending_packets)

        while not self.resend_queue.empty():
            if space > 0:
                self.resend_packet()
            else:
                break
        while not self.send_queue.empty():
            if space > 0:
                self.send_packet()
            else:
                break

    def resend_packet(self):
        """
        If there are any packets that have timed out, send the one with the lowest
        sequence number
        """
        seq, packet = self.resend_queue.get()
        if len(packet) <= self.MSS:
            self.socket.send(packet.build())
            self.sending_packets.add((packet, datetime.datetime.now(), True))

    def send_packet(self):
        """
        If there is any data to send, send a packet containing it.
        """
        # Get data
        if not self.connected:
            return
        else:
            # Send a packet of data or ack another packet.
            packet_data = b''
            while not self.send_queue.empty() and len(packet_data) < self.MSS:
                packet_data += self.send_queue.get()

            # Create packet
            packet = TCPPacket(self.src, self.dest, self.seq, self.next_packet['next_expected_seq'], packet_data)
            packet.ack = 1
            packet.checksum()
            # Track that we're sending this packet.
            self.sending_packets.add((packet, datetime.datetime.now(), False))
            # Send packet
            self.socket.send(packet.build())
