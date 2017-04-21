#!/usr/bin/python


import socket
import struct

class dnsanswer:
    def __init__(self,name,data,type=0x0001,cla=0x0001,ttl=0xff):
        '''
        :param self:
        :param name: the domain name being queried
        :param data: the data of the response
        :param type: 0x0001 indicates A record 0x0005 indicates CNAME
        :param cla: short for class, 0x0001 indicates Internet address
        :param ttl: number of seconds the result can be cached
        :return:
        '''
        self.name=name
        self.type=type
        self.cla=cla
        self.ttl=ttl
        self.data=data
        self.rdlength=0 #the length of the data



    def to_binary(self):
        '''
        :return: The binary representation of the answer part
        '''
        #ToDo: I do not think anything needs to be done on name

        binary_domain = b''
        for label in self.name.split("."):
            binary_domain += chr(len(label)).encode()
            binary_domain += label.encode()
        binary_domain += b'\x00'

        ip=socket.inet_aton(self.data)
        self.rdlength=len(ip)
        return  binary_domain+struct.pack("!HHIH",self.type,self.cla,self.ttl,self.rdlength)+ ip
