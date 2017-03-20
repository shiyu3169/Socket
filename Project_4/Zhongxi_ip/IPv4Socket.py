import threading
import socket
import queue

from IPv4Packet import IPv4Packet


class IPv4Socket:
    def __init__(self, address):
        self.is_connected=False

        self.send_socket=None
        self.receive_socket=None

        self.destionation_ip=None
        self.source_ip=None

        self.complete_packets_queue=queue.Queue()
        self.partial_packets_buffer={}
        self.current_packet_unfinished=None

        self.listening_thread=None

    def connect(self, destination):
        '''

        :param destination: destination[0] is destination's link, destination[1] is the socket
        :return: None
        '''
        self.is_connected=True
        try:
            self.receive_socket=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_TCP)
            self.receive_socket.setblocking(False)
            self.send_socket=socket.socket(socket.SOCK_RAW,proto=socket.IPPROTO_RAW)
            self.send_socket.connect(destination)
        except:
            raise Exception("sockets cannot be correctly initiated for connection")

        try:
            self.destionation_ip=socket.gethostbyname(destination[0])
        except:
            raise Exception("the ip address for the link cannot be found")


        try:
            self.thread=threading.Thread(target=self.loop_for_incoming_data)
            self.thread.setDaemon(True)
            self.thread.start()
        except:
            raise Exception("Listening thread cannot be initiated correctly")



    def terminate(self):
        self.is_connected=False
        try:
            self.receive_socket.shutdown()
            self.receive_socket.close()
            self.send_socket.shutdown()
            self.send_socket.close()
        except:
            raise Exception("sockets cannot be correctly closed")




    def loop_for_incoming_data(self):
        while 1:
            if not self.is_connected:
                break;
            try:




    #ToDo: change the name to recv_data
    def recv(self,max_size=IPv4Packet.PACKET_MAX_SIZE):



    #ToDo: change the name to send_data
    def send(self,data):

