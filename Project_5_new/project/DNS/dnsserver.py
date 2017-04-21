#!/usr/bin/python


import socket
from dnspacket import dnspacket
import argparse
import random
import Queue as queue
from georank import *
import threading


MAX_PACKET_SIZE=65535
SERVERS=[
    '52.90.80.45',
    '54.183.23.203',
    '54.70.111.57',
    '52.215.87.82',
    '52.28.249.79',
    '54.169.10.54',
    '52.62.198.57',
    '52.192.64.163',
    '54.233.152.60'
]


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
        self.ip_to_target_ip_distance={}
        self.ip_to_query=queue.Queue()
        self.thread=threading.Thread(target=self.loop)
        self.thread.setDaemon(True)
        try:
            #ToDo: another way to bind with empty ip address?
            self.socket.bind(("",self.port))
        except:
            raise Exception("The port is occupied")

    def listen_and_response(self):
        '''
            An infinite loop to always listen for incoming dns queries,
                return the ip address of one of the EC2 server.

            The query must be the same as self.domain, otherwise the dns
            server would not reply.
        '''
        query_times=0
        while True:
            try:
                data, address=self.socket.recvfrom(MAX_PACKET_SIZE)
            except:
                raise Exception("Cannot get packets")
            try:
                [qname,request]=dnspacket.unpack(data)
                if qname!=self.domain:
                   continue
            except:
                raise Exception("Unable to unpack data")
            response=dnspacket()
            response.id=request.id

            query_times+=1
            print(query_times)
            try:
                best_replica_ip=self.find_best_replica(address)
            except:
                raise Exception("unable to find best replica")
            response.set_answer(self.domain, best_replica_ip)
            try:
                self.socket.sendto(response.pack(),address)
            except:
                raise Exception("Unable to send")


    def find_best_replica(self,address):
        '''
        :param address: the ip address of the client which makes the dns request
        :return: the ip address of the replica for this client
        '''

        client_ip=address[0]
        if client_ip in self.ip_to_target_ip_distance:
            result_ip= (self.ip_to_target_ip_distance[client_ip])[0]
            return result_ip
        else:
            self.ip_to_query.put(client_ip)
            return random.choice(SERVERS)


    def loop(self):
        '''
            The loop being run in the separated thread, taking one ip from the ip_to_query queue,
            find its geolocation and distances to all the EC2, put this IP and the closet EC2's ip
             and distance into the dictionary ip_to_target_ip_distance
        '''

        while True:
            if not self.ip_to_query.empty():
                current_ip=self.ip_to_query.get()
                result=get_distances(current_ip)
                smallest_ip_distance=sorted(result.items(), key=lambda x: x[1])[0]
                if not current_ip in self.ip_to_target_ip_distance:
                    self.ip_to_target_ip_distance[current_ip]=smallest_ip_distance
                elif self.ip_to_target_ip_distance[current_ip][1]>smallest_ip_distance[1]:
                    self.ip_to_target_ip_distance[current_ip]=smallest_ip_distance



def main(args):
    server=dnsserver(args.name,args.portNumber)
    try:
        server.thread.start()
        server.listen_and_response()
    except:
        raise Exception("DNS server is terminated")



if __name__=="__main__":
    parser=argparse.ArgumentParser(description='Process input')
    parser.add_argument("-p","--portNumber",type=int,choices=range(40000,65535))
    parser.add_argument("-n","--name",type=str)
    args=parser.parse_args()
    main(args)




