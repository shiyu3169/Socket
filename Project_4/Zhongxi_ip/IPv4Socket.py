import threading
import socket
import queue

from Zhongxi_ip.IPv4Packet import IPv4Packet


class IPv4Socket:
    def __init__(self, address):


    def connect(self, destination):

    def terminate(self):

    def loop_for_incoming_data(self):

    #ToDo: change the name to recv_data
    def recv(self,max_size=IPv4Packet.PACKET_MAX_SIZE):

    #ToDo: change the name to send_data
    def send(self,data):

