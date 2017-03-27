#! /usr/bin/python3


import threading
import socket
import queue

from IP.IPPacket import IPPacket


class IPSocket:

    LOCAL_HOST_IP="127.0.0.1"


    def __init__(self, source_address):
        self.is_connected=False

        self.send_socket=None
        self.receive_socket=None

        self.destionation_ip=None
        self.source_ip=source_address

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
            self.send_socket=socket.socket(type=socket.SOCK_RAW,proto=socket.IPPROTO_RAW)
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





    def loop_for_incoming_data(self):
        while 1:
            if not self.is_connected:
                break;
            try:
                response=self.receive_socket.recvfrom(IPPacket.PACKET_MAX_SIZE)
            except Exception:
                continue
            new_packet=IPPacket.generate_packet_from_received_bytes(response[0])

            if new_packet.destination_ip not in [IPSocket.LOCAL_HOST_IP, self.source_ip] or \
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



    def recv(self,max_size=IPPacket.PACKET_MAX_SIZE):
        packet=None
        if self.current_packet_unfinished is None:
            if not self.complete_packets_queue.empty():
               packet= self.complete_packets_queue.get(False)
            return packet
        else:
            packet=self.current_packet_unfinished

        if len(packet)<=max_size:
            result=packet
            self.current_packet_unfinished=None
        else:
            result=packet[:max_size]
            self.current_packet_unfinished=packet[max_size:]

        return result





    def send(self,data):
        new_packet=IPPacket(self.source_ip,self.destionation_ip,data)
        new_packet.set_checksum_field()
        #print(new_packet.checksum())
        self.send_socket.send(new_packet.convert_packet_to_bytes())
