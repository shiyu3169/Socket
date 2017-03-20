import random
import datetime
import time
import fcntl
from ip.IPSocket import *
from tcp.TCPPacket import *


def get_ip(ifname='eth0'):
    """
    Get ip address of the source, only works for linux machine
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = struct.pack('256s', ifname[:15].encode())
    ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, data)[20:24])
    return ip

ALPHA = 0.875  # NEW_RTT = ALPHA * OLD_RTT + (1 - ALPHA) * PACKET_RTT


class STATE:
    NEW = 0
    SYN_SENT = 1
    OPEN = 2
    FIN_SENT = 3
    CLOSED = 4
    RST = 5
    RST_RECEIVED = 6
    FIN_RECEIVED = 7


class TCPSocket:
    """
    This class is an implementation of TCP built on a custom
    implementation of IP.  It functions as any old socket would.
    """
    def __init__(self):
        self.socket = None
        self.src = (get_ip(), random.randrange(0, 1 << 16))
        self.state = STATE.NEW
        self.thread = None
        self.data_send_queue = queue.Queue()
        self.data_recv_queue = queue.Queue()

    def connect(self, dest):
        """
        Create a new connection
        """
        # Connection State
        self.socket = IPSocket(get_ip())
        self.socket.connect(dest)
        self.dest = (socket.gethostbyname(dest[0]), dest[1])

        # I/O
        self.current_recv_packet = None

        # The slow start threshold.
        self.ss_thresh = float("inf")

        # This is the congestion window here.
        self.congestion_window = 1

        # This is the advertised window at the destination.
        self.dest_window = float('inf')

        # Round Trip Time in ms
        self.RTT = None

        # The Max Segment Size.  The default is 536 = 576 - IP_HEADER - TCP_HEADER
        self.MSS = 536

        # This contains information regarding how the next packet should look.
        self.next_packet = {
            'ack_num': 1,
            'ack': 0,
            'seq': random.randrange(0, 1 << 32)
        }

        # This is the remainder of the data for a packet that we already sent part of.
        self.current_send_packet = None

        # This is the collection of packets that are currently in the network.
        self.packets_in_network = set()

        # This is a queue of packets which must be resent, sorted into seq number order
        self.resend_queue = queue.PriorityQueue()

        # This is the seq number that needs to be acked to move the window.
        self.seq = 0

        self.out_of_order_packets = queue.PriorityQueue()
        self.seen_seq_nums = set()

        # start the thread
        self.handshake()

        self.thread = threading.Thread(name="tcp-loop", target=self.loop)
        self.thread.setDaemon(True)
        self.thread.start()

    def send(self, data):
        """
        Send some data over the network. The same as sendall.
        """
        self.data_send_queue.put(data)

    def sendall(self, data):
        """
        Send all the data over the socket.
        """
        self.send(data)


    def recv(self, max_bytes=None):
        """
        Get data from the socket
        """
        packet = b''
        if self.state == STATE.RST:
            raise Exception("Socket closed")

        if self.current_recv_packet is None:
            while True:
                if self.state == STATE.RST:
                    raise Exception("Socket closed")
                if not self.data_recv_queue.empty():
                    packet += self.data_recv_queue.get(block=False)
                    time.sleep(0)
                else:
                    break
            if max_bytes is not None and len(packet) > max_bytes:
                self.current_recv_packet = packet[max_bytes:]
                packet = packet[:max_bytes]
        else:
            packet = self.current_recv_packet
            if max_bytes is None or len(packet) <= max_bytes:
                self.current_recv_packet = None
            else:
                self.current_recv_packet = packet[max_bytes:]
                packet = packet[:max_bytes]

        return packet


    def close(self):
        """
        Sent the shutdown signal to clean up the connection
        """
        self.next_packet['fin'] = 1
        p = TCPPacket(self.src, self.dest, 0, self.seq)
        p.fin = 1
        p.checksum()
        self.socket.send(p.to_bytes())

    def loop(self):
        """
        Thread target for running TCP separate from application.
        """

        while self.state != STATE.CLOSED:
            self.send_new_packets()

            while True:
                packet = self.socket.recv()
                if packet is not None:
                    self.parse_packet(packet)
                else:
                    break

            if self.state == STATE.RST_RECEIVED or self.state == STATE.FIN_RECEIVED:
                self.close()
                break

            self.check_timeouts()

            # Gotta avoid busy wait
            time.sleep(50.0 / 1000)

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
        self.socket.send(syn.to_bytes())

        # Get packets until we see a SYN_ACK from the destination to us.
        while True:
            p = self.socket.recv()
            if p is None:
                continue
            p = TCPPacket.build(p, self.dest[0], self.src[0])
            if p.src == self.dest and p.dest == self.src and p.syn and p.ack:
                break
            time.sleep(10.0 / 1000)

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
        self.socket.send(ack.to_bytes())

        self.state = STATE.OPEN

    def parse_packet(self, packet):
        """
        Convert the packet to an object.
        """
        packet = TCPPacket.build(packet, self.dest[0], self.src[0])

        # Check validity
        if not packet.is_valid(self.dest, self.src):
            return

        # Pull out MSS Information
        for o in packet.options:
            if o['kind'] == 2 and o['length'] == 4:
                self.MSS = o['value']
                break

        # Handle ACK
        if packet.ack and packet.ack_num >= self.seq:
            self.handle_ack(packet)

        # ACK this packet if it contains data or FIN or SYN
        if (len(packet.data) > 0) or packet.syn:
            self.next_packet['ack'] = 1

        # Update the next expected seq number
        next_seq = packet.seq + len(packet.data)
        if len(packet.data) > 0 and packet.seq == self.next_packet['next_expected_seq']:
            # This is the packet we need.
            self.next_packet['next_expected_seq'] = next_seq
            self.data_recv_queue.put(packet.data)
            while not self.out_of_order_packets.empty():
                p = self.out_of_order_packets.get()
                if p.seq == next_seq:
                    self.data_recv_queue.put(p.data)
                    next_seq = p.seq + len(p.data)
                else:
                    self.out_of_order_packets.put(p)
                    break
        elif len(packet.data) > 0 and packet.seq > self.next_packet[
            'next_expected_seq'] and packet.seq not in self.seen_seq_nums:
            # Packet is too early, store it.
            self.out_of_order_packets.put(packet)
            self.seen_seq_nums.add(packet.seq)

        # Ack the packet if it has data
        if self.next_packet['ack']:
            p = TCPPacket(self.src, self.dest, self.seq, self.next_packet['next_expected_seq'])
            p.ack = 1
            p.checksum()
            self.socket.send(p.to_bytes())

        self.dest_window = packet.window

        if packet.fin:
            self.state = STATE.FIN_RECEIVED
        elif packet.rst:
            self.state = STATE.RST_RECEIVED

    def handle_ack(self, packet):
        """
        Handles the ACK clocking part of TCP.
        """
        # Increase the congestion window.
        if self.congestion_window < self.ss_thresh:
            self.congestion_window += 1
        else:
            self.congestion_window += 1 / self.congestion_window

        self.seq = packet.ack_num

        # Find packets that were just acked.
        acked_packets = set()

        for p in self.packets_in_network:
            if p[0].seq <= self.next_packet['seq']:
                acked_packets.add(p)

        # Remove them from the packets in the network
        self.packets_in_network.difference_update(acked_packets)

        # Manage their RTTs.
        now = datetime.datetime.now()
        for p in acked_packets:
            if not p[2]:
                # Packet didn't time out so it's valid for RTT calculation
                packet_rtt = now - p[1]
                if self.RTT is None:
                    self.RTT = packet_rtt.total_seconds() * 1000
                else:
                    self.RTT = ALPHA * self.RTT + (1 - ALPHA) * packet_rtt.total_seconds() * 1000

    def check_timeouts(self):
        """
        Check to see if any previously sent packets have timed out while waiting to be
        ACKed
        """
        if self.RTT is None:
            return

        timeout_packets = []
        now = datetime.datetime.now()
        for p in self.packets_in_network:
            dt = (now - p[1]).total_seconds() * 1000
            if dt > 2 * self.RTT:
                timeout_packets.append(p)

        if len(timeout_packets) > 0:
            self.ss_thresh = self.congestion_window / 2
            self.congestion_window = 1

            for p in timeout_packets:
                self.packets_in_network.remove(p)
                self.resend_queue.put((p[0].seq, p[0]))

    def send_new_packets(self):
        """
        Send new packets containing the data passed into the socket via send,
        and resend timed out packets. Do so until the window if full.
        """
        space = min(self.congestion_window, self.dest_window) / self.MSS - len(self.packets_in_network)

        while not self.resend_queue.empty() and space > 0:
            self.resend_packet()

        while not self.data_send_queue.empty() and space > 0:
            self.send_new_packet()

    def resend_packet(self):
        """
        If there are any packets that have timed out, send the one with the lowest
        sequence number
        """
        seq, packet = self.resend_queue.get()

        max_packet_size = self.MSS

        if len(packet) <= max_packet_size:
            self.socket.send(packet.to_bytes())
            self.packets_in_network.add((packet, datetime.datetime.now(), True))
            self.current_resend_packet = None
        else:
            self.current_resend_packet = packet

    def send_new_packet(self):
        """
        If there is any data to send, send a packet containing it.
        """

        # Get data
        if self.state == STATE.OPEN:
            # Send a packet of data or ack another packet.
            packet_data = b''
            while not self.data_send_queue.empty() and len(packet_data) < self.MSS:
                packet_data += self.data_send_queue.get()

            # Create packet
            packet = TCPPacket(self.src, self.dest, self.seq, self.next_packet['next_expected_seq'], packet_data)
        else:
            return

        packet.ack = True

        packet.checksum()
        packet_bytes = packet.to_bytes()

        # Track that we're sending this packet.
        self.packets_in_network.add((packet, datetime.datetime.now(), False))

        # Send packet
        self.socket.send(packet_bytes)
