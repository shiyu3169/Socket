import threading
import socket
import queue

from IPv4Packet import IPv4Packet


class IPv4Socket:

    LOCAL_HOST_IP="127.0.0.1"


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



    #ToDo: It looks this function is never used in DASHEN's code
    def shutdown(self):
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
                response=self.receive_socket.recvfrom(IPv4Packet.PACKET_MAX_SIZE)
            except:
                print("Error happens when reading from socket")
            new_packet=IPv4Packet.generate_packet_from_received_bytes(response[0])

            if new_packet.destination_ip not in [IPv4Socket.LOCAL_HOST_IP, self.source_ip] or \
                new_packet.source_ip!=self.destionation_ip:
                print("Drop a packet destined for the wrong address")
                continue

            if new_packet.checksum()!=0:
                #ToDo: if the checksum is wrong, does it make sense to continue parsing it?
                print("Drop a packet whose checksum does not match header")
            if new_packet.fragment_offset==0 and new_packet.flag_more_fragments==0:
                self.complete_packets_queue.put(new_packet.data)
            elif new_packet.flag_more_fragments==1:
                if new_packet.id not in self.partial_packets_buffer:
                    new_queue=queue.PriorityQueue()
                    new_queue.put((new_packet.fragment_offset, new_packet))
                    self.partial_packets_buffer[new_packet.id]=new_queue
                else:
                    self.partial_packets_buffer[new_packet.id].put((new_packet.fragment_offset, new_packet))
                    self.assemble_if_complete(new_packet.id)


    def assemble_if_complete(self,id):
        queue_for_packet= self.partial_packets_buffer[id].copy()
        last_index=0
        data=b''
        while not queue_for_packet.empty():
            current_partial_packet=queue_for_packet.get()
            if last_index!=current_partial_packet.fragment_offset:
                return
            last_index += (current_partial_packet.total_length-current_partial_packet.ihl*4)/8
            data+=current_partial_packet.data
        del self.partial_packets_buffer[id]
        self.complete_packets_queue.put(data)


    '''
    def assemble_packet(self,id):
        data=b''
        queue_for_packet=self.partial_packets_buffer[id]
        while not queue_for_packet.empty():
            current_partial_packet=queue_for_packet.get()
            data+=current_partial_packet.data
        del self.partial_packets_buffer[id]
        self.complete_packets_queue.put(data)
    '''


    #ToDo: change the name to recv_data
    def recv(self,max_size=IPv4Packet.PACKET_MAX_SIZE):



    #ToDo: change the name to send_data
    def send(self,data):
        #ToDo: all the outgoing packet has checksum field as 0, no good

