import argparse
import errno
import os
import subprocess
import socket
from random import randint



SERVER_ADDRESS = 'localhost', 8888
REQUEST = b"""\
GET /w/index.php?search=hello&button=&title=Special%3ASearch  HTTP/1.1
Host: localhost:8888

"""


def main(max_clients, max_conns):
    names = []
    f = open('HTTP/pathname', 'r')
    line = f.readline()
    while line != "":
        name = line.strip()
        names.append(name)
        line = f.readline()
    socks = []
    for client_num in range(max_clients):
        pid = os.fork()
        if pid == 0:
            for connection_num in range(max_conns):
                '''
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(SERVER_ADDRESS)
                sock.sendall(REQUEST)
                socks.append(sock)'''
                random_number=randint(0,len(names)-1)
                os.system("wget ec2-54-166-234-74.compute-1.amazonaws.com:8080/wiki/"+names[random_number])
                print(connection_num)
                os._exit(0)


if __name__ == '__main__':
   parser = argparse.ArgumentParser(
       description='Test client for LSBAWS.',
       formatter_class=argparse.ArgumentDefaultsHelpFormatter,
   )
   parser.add_argument(
       '--max-conns',
       type=int,
       default=1024,
       help='Maximum number of connections per client.'
   )
   parser.add_argument(
       '--max-clients',
       type=int,
       default=1,
       help='Maximum number of clients.'
   )
   args = parser.parse_args()
   main(args.max_clients, args.max_conns)