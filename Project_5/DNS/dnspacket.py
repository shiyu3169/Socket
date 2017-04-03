import struct

class DNS_Packet:
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
        self.questions=[]
        self.ancount=[]


    def pack(self):
        '''
        :return: the binary representation of the header

        Since no question will be asked by this server, the question field of the packet is ignored
        '''

        #ToDo: probably only one answer is needed
        answers=b''
        for answer in self.answers:
            answers+=answer.to_binary()

        self.ancount=len(answers)

        header=struct.pack("!HHHHHH",self.id,self.flag,self.qdcount,self.ancount,self.nscount,self.arcount)

        return header+answers


    @classmethod
    def response_packet(cls,data):
        packet=cls()
        header=struct.unpack("!HHHHHH",data[:12])
        packet.id=header[0]
        #ToDo: line55 probably is not needed
        packet.flag=header[1]
        #what about the data after the first 12 bytes
        return packet


    def add_answer(self,URL,data):
        answer=dnsanswer(URL,data)
        self.answers.append(answer)



