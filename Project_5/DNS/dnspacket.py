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

        answer_in_byte=self.answer.to_binary()

        self.ancount=len(answer_in_byte)

        header=struct.pack("!HHHHHH",self.id,self.flag,self.qdcount,self.ancount,self.nscount,self.arcount)

        return header+answer_in_byte


    @classmethod
    def unpack(cls,data):
        packet=cls()
        header=struct.unpack("!HHHHHH",data[:12])
        question=data[12:]
        [qtype,qclass]=struct.unpack('>HH',question[-4:])
        s = question[:-4]
        pointer = 0
        temp = []
        while True:
            count = ord(s[pointer])
            if count == 0:
                break
            pointer += 1
            temp.append(s[pointer:pointer + count])
            pointer += count
        qname = '.'.join(temp)
        packet.id=header[0]
        return [qname,packet]


    def set_answer(self, URL, data):
        answer=dnsanswer(URL,data)
        self.answer=answer



