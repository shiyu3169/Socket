#!/usr/bin/python


import socket
from dnspacket import dnspacket
import argparse
from georank import *

MAX_PACKET_SIZE=65535

class dnsserver:

    def __init__(self,domain,port):
        '''
        Initializer for this class
        :param domain: the domain name for this dns server
        :param port: The port the dnssever listen on
        '''
        self.domain=domain
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.port=port
        #ToDo:what is this line doing?
        try:
            #ToDo: another way to bind with empty ip address?
            self.socket.bind(("",self.port))
        except:
            raise Exception("The port is occupied")

    def listen_and_response(self):
        '''
            An infinite loop to always listen for incoming dns queries,
                what ever the query is, return the ip address of one of
                the EC2 server
        '''
        while True:
            data, address=self.socket.recvfrom(MAX_PACKET_SIZE)
            request=dnspacket.unpack(data)
            response=dnspacket()
            response.id=request.id
            best_replica_ip=self.find_best_replica(address)
            #ToDo: add_answer first parameter should not be the domain name in question?
            response.set_answer(self.domain, best_replica_ip)
            self.socket.sendto(response.pack(),address)


    def find_best_replica(self,address):
        '''
        :param address: the ip address of the client which makes the dns request
        :return: the ip address of the replica for this client
        '''
        result_map=get_distances(address[0])
        return sorted(result_map.items(), key=lambda x: x[1])[0][0]



def main(args):
    server=dnsserver(args.name,args.portNumber)
    try:
        server.listen_and_response()
    except:
        raise Exception("DNS server is terminated")



if __name__=="__main__":
    parser=argparse.ArgumentParser(description='Process input')
    parser.add_argument("-p","--portNumber",type=int,choices=range(40000,65535))
    parser.add_argument("-n","--name",type=str)
    args=parser.parse_args()
    main(args)




