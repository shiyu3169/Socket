import struct
import socket
from random import randint

def cyclic_generator():
    present=randint(0,0xffff)
    while 1:
        yield present
        present=(present+1)&0xffff

ID_GENERATOR=cyclic_generator()


class IPv4Packet:

    PACKET_MIN_SIZE=20
    PACKET_MAX_SIZE=65535

    def __init__(self,source,destination,data):


        '''
        :param source: The source's IPv4 address
        :param destination:  The destination's IPv4 address
        :param data: binary data
        '''

        #The header fields of IPv4 (reference: Wiki IPv4 header)

        #zeroth word (except total length)
        self.version=4
        self.ihl=5
        self.dscp=0
        self.ecn=0

        #first word
        self.id=next(ID_GENERATOR,0)
        self.flag_reserved=0
        self.flag_dont_fragment=0
        self.flag_more_fragments=0
        self.fragment_offset=0

        #second word
        self.ttl=128
        self.protocol=6 #ToDo: is 6 correct?
        self.header_checksum=0

        #third word
        self.source_ip=source

        #fourth word
        self.destination_ip=destination

        #fifth to eighth words
        self.options=None #only exist if self.ihl>5

        self.data=data

        self.total_length=self.ihl*4

        try:
            self.total_length+=len(self.data)
        except:
            print("Data of current packet is empty or not in the correct form (byte literal)")


    @classmethod
    def generate_packet_from_received_bytes(cls,bytes):
        if len(bytes)<IPv4Packet.PACKET_MIN_SIZE:
            print("Not enough bytes to build a packet") #ToDo: should the message just be printed or raised as an Exception
            return None
        elif len(bytes)>IPv4Packet.PACKET_MAX_SIZE:
            print("Too many bytes for one packet") #ToDo: should the message just be printed or raised as an Exception
            return None

        first_five_words_of_header=struct.unpack("!BBHHHBBH4s4s",bytes)
        source_ip_of_bytes=first_five_words_of_header[8]
        destination_ip_of_bytes=first_five_words_of_header[9]
        temporary_data=b""
        packet_generated_from_bytes=cls(socket.inet_ntoa(source_ip_of_bytes),
                                        socket.inet_ntoa(destination_ip_of_bytes),
                                        temporary_data)
        packet_generated_from_bytes.version=first_five_words_of_header[0]>>4
        packet_generated_from_bytes.ihl=first_five_words_of_header[0]& 0x0f
        packet_generated_from_bytes.dscp=first_five_words_of_header[1]>>2
        packet_generated_from_bytes.ecn=first_five_words_of_header[1]& 0x03
        packet_generated_from_bytes.total_length=first_five_words_of_header[2] & 0xffff






    def convert_packet_to_bytes(self):






    def checksum(self):

