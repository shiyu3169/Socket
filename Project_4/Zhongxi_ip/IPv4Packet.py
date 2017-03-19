import socket
import socket
from random import randint

def cyclic_generator():
    present=randint(0,0xffff)
    while 1:
        yield present
        present=(present+1)&0xffff

ID_GENERATOR=cyclic_generator()


class IPv4Packet:
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
            raise Exception("Data of current packet is empty or not in the correct form (byte literal)")


