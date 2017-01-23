import socket


__author__="Zhongxi Wang"


def connect_server(isSecure,serverName,portNumber):
    clientSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    #ToDo: isSecure should do SSL

    clientSocket.connect((serverName,portNumber))
    return clientSocket


def message_parser(message):


def loop_for_all_cases(clientSocket,clientMessage):
    clientSocket.send(clientMessage.encode())
    receivedMessage=clientSocket.recv(2048).decode()


def main(args):
    print("Nothing")


if __name__=="__main__":
    clientSocket=connect_server(False,"cs5700sp17.ccs.neu.edu",27993)
    parse_Message(clientSocket,'cs5700spring2017 HELLO 001156814\n')
