#! /usr/bin/python3

import sys
from HTTP.CookieJar import CookieJar


class ServerMessage:
    """this is a model that parsing received message from HTTP server"""

    def __init__(self, my_socket):
        """
        Initialize this message and read the data from the network.
        This should probably be refactored somehow.
        :param sock: The socket to read this message from.
        """
        self.version = ""
        self.status_code = None
        self.headers = {}
        self.body = b""
        self.cookieJar = CookieJar()

        # Start reading received message and update variables
        self.get_status(my_socket)
        self.read_headers(my_socket)
        if "transfer-encoding" in self.headers and self.get_header("transfer-encoding") == "chunked":
            self.read_chunked_body(my_socket)
        else:
            bodyLength = int(self.get_header("content-length"))
            self.read_body(my_socket, bodyLength)

    def get_status(self, file):
        """read the first line to get status info"""
        try:
            statusLine = readline(file).decode()
        except:
            raise Exception("Error in reading line")
            # check if the file is empty, raise exception
        if statusLine == "":
            raise Exception("socket is empty")

        try:
            version, status_code, status = statusLine.split(None, 2)
            self.version = str(version)
            self.status_code = str(status_code)
            self.status = str(status)
        except:
            raise Exception("Status line of response message is problematic")

    def read_headers(self, file):
        """start reading the 2nd line of header"""
        key = ""
        while 1:
            try:
                line = readline(file).decode("utf-8")
            except:
                raise Exception("Error in reading line")

            if line is None:
                raise Exception("Error read line")
            elif ":" not in line:
                # valid header line is supposed to always have ":" symbol
                break

            # remove leading space
            sLine = str(line.strip())

            if line[0] is " ":
                if str(key.lower()) == "set-cookie":
                    self.cookieJar.add_cookie_from_string(str(sLine))
                self.headers[str(key.lower())] = str(sLine)
                continue
            try:
                key, value = sLine.split(":", 1)
            except:
                raise Exception("invalid format of header")

            if str(key.lower()) == "set-cookie":
                self.cookieJar.add_cookie_from_string(str(value.strip()))
            self.headers[str(key.lower())] = str(value.strip())

    def read_body(self, file, fileLength):
        """Read the body of the message"""
        self.body = b""
        num = 0
        sys.stdout.write("\r{:d}%".format(int(float(num) / fileLength * 100)))
        while True:
            data = file.recv(fileLength)
            if data is None:
                raise Exception("empty socket")
            data = data
            num += len(data)
            self.body += data
            sys.stdout.write("\r{:d}%".format(int(float(num) / fileLength * 100)))
            if num >= fileLength:
                break
        sys.stdout.write("\n")

    def read_chunked_body(self, file):
        """Read a chunked body."""
        print("Reading Chunked message")
        while 1:
            try:
                hexsize = readline(file).decode("utf-8")
            except:
                raise Exception("Error reading a line in chunked body")
            hexsize = hexsize.strip()
            size = int(hexsize, 16)
            if size == 0:
                break
            data = b""
            while True:
                try:
                    line = file.recv(size)
                except:
                    raise Exception("Error reading a line in chunked body")
                data += line
                size -= len(line)
                if size <= 0:
                    break
            self.body += data
            file.recv(2)  # read line \r\n
        self.read_headers(file)

    def get_header(self, key):
        """Get a header from this message"""
        try:
            return self.headers[key]
        except KeyError:
            raise Exception("Missing Header")


def readline(file):
    """
    read the data in this line
    :return:
    """
    line = b""
    c = None
    while True:
        c = file.recv(1)
        line += c
        if c == b"\n":
            break
    return line