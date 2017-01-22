#!/usr/bin python

import socket
import sys
import ssl
import argparse
import re
# Math function used to calculate math expressions
def math(values):
    # Cast string into int
    a = int(values[2])
    b = int(values[4])
    operator = values[3]

    if operator is '+':
        answer = a + b
    elif operator is '-':
        answer = a - b
    elif operator is '*':
        answer = a * b
    elif operator is '/':
        answer = a // b
    else:
        assert 'operator error'
    return str(answer)

# Main function
def main(args):

    # default variables
    port = 27993
    crn = "cs5700spring2017 "

    # varibales from command line input
    hostname = args[-2]
    nuid = args[-1]

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Check if '-s' is in input
    if '-s' in args:
        port = 27994
        sock = ssl.wrap_socket(sock)

    # check if port is given in input
    if '-p' in args:
        port = int(args[args.index('-p') + 1])

    # Connect the socket to the port where the server is listening
    # print "connect to the server"
    server_address = (hostname, port)
    # print >> sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

    # Send hello message to server
    hello = crn + "HELLO " + nuid + "\n"
    sock.send(hello)

    # Receive the Status message from server
    status = sock.recv(256)
    values = status.split()
    # print status

    # Calculate result value
    while (len(values) > 0):
        # If the replay message is BYE, close the socket
        if (values[2] == 'BYE'):
            print values[1] # print the secret flag
            sock.close()
            break

        # Calculate
        else:
            result = crn + math(values) + " \n"
            sock.send(result)
            status = sock.recv(1024)
            # print status
            values = status.split()


# Initializer
if __name__ == "__main__":
    parser.add_argument("-p", "--port", help="The server port to connect to", type=int, default=27993)
    parser.add_argument("-s", "--secure", help="Use a secure socket", action='store_true')
    parser.add_argument("hostname", help="The hostname of the server")
    parser.add_argument("id", help="The NEU id of the student running the program.  Must have all leading zeros.")
    main(sys.argv)