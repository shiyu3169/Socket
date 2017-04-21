#!/usr/bin/python


import struct
from dnsanswer import dnsanswer

class dnspacket:
    def __init__(self):
        '''
        Initiate the class

        self.flag=0x8400 corresponds to

        QR=True
        Opcode=0
        AA(authoritative)=True
        TC(truncate)=False
        RD(Recursive Desired)=False
        RA(Recurivse Available)=False
        Z=0
        RCODE=0
        '''

        self.id=0 #16 bits
        self.flag=0x8400 #16bits
        self.qdcount=0 #16bits
        self.ancount=0 #16bits
        self.nscount=0 #16bits
        self.arcount=0 #16bits
        self.question=None
        self.answer=None


    def pack(self):
        '''
        :return: the binary representation of the header

        Since no question will be asked by this server, the question field of the packet is ignored
        '''

        question_in_byte=b''

        answer_in_byte=self.answer.to_binary()

        self.ancount=1 #there is only one answer

        header=struct.pack("!HHHHHH",self.id,self.flag,self.qdcount,self.ancount,self.nscount,self.arcount)

        return header+question_in_byte+answer_in_byte


    @classmethod
    def unpack(cls,data):
        '''
        :param data: the binary data of dns query from socket
        :return: the url the query is for and the reconstructed pakcet
        '''

        packet=cls()
        header=struct.unpack("!HHHHHH",data[:12])
        packet.id=header[0]

        #This part is to extract the url the query is asking about
        question=data[12:]
        [qtype,qclass]=struct.unpack('>HH',question[-4:])
        qname_binary = question[:-4]
        pointer = 0
        temp = []
        while True:
            count = ord(qname_binary[pointer])
            if count == 0:
                break
            pointer += 1
            temp.append(qname_binary[pointer:pointer + count])
            pointer += count
        qname = '.'.join(temp)
        return [qname,packet]


    def set_answer(self, URL, data):
        answer=dnsanswer(URL,data)
        self.answer=answer



