import sys
from HTTP.CookieJar import CookieJar


class ServerMessage:
    """this is a model that parsing received message from HTTP server"""

    def __init__(self, my_socket):
        """initialize the variables"""
        self.version = ""
        self.status_code = None
        self.status = ""
        self.cookieJar = CookieJar()
        self.headers = {}
        self.body = b""

        # Start reading received message and update variables
        file = my_socket
        self.get_status(file)
        self.read_headers(file)
        if "transfer-encoding" in self.headers and self.get_header("transfer-encoding") == "chunked":
            self.read_chunked_body(file)
        else:
            bodyLength = int(self.get_header("content-length"))
            self.read_body(file, bodyLength)

    def get_status(self, file):
        """read the first line to get status info"""
        try:
            statusLine = readline(file).decode("utf-8").strip()
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
        """
        Read the body of the message. This should be done if the message
        has a body and the transfer-encoding header is not "chunked".
        :param size: The size of the body in bytes
        :param socket_reader: The file to read the body from.
        """
        self.body = b""
        num = 0
        progress_bar(num, fileLength)
        while True:
            data = file.recv(fileLength)
            if data is None:
                raise Exception("empty socket")
            data = data
            num += len(data)
            self.body += data
            progress_bar(num, fileLength)
            if num >= fileLength:
                break
        sys.stdout.write("\n")

    def read_chunked_body(self, file):
        """
        Read a chunked body.  This should be called when the transfer-encoding of the
        message is "chunked"
        :param file: The file to read this from.
        """
        print("Reading Chunked message, No file length")
        body = b""
        while 1:
            try:
                hexsize = readline(file).decode("utf-8")
            except:
                raise Exception("Error reading a line in chunked body")
            if hexsize is None:
                raise Exception("Empty Socket")
            hexsize = hexsize.strip()
            size = int(hexsize, 16)
            if size == 0:
                break
            data = b""
            while 1:
                try:
                    line = file.recv(size)
                except:
                    raise Exception("Error reading a line in chunked body")
                data += line
                size -= len(line)
                if size <= 0:
                    break
            file.recv(2) # read line \r\n
        self.body += data
        self.read_headers(file)

    def get_header(self, key):
        """
        Get a single header from this message
        :param key: The key for the header. Should be lower-case.
        :return: The value of this header
        :except: MissingHeaderException if the header does not exist.
        """
        try:
            return self.headers[key]
        except KeyError:
            raise Exception("Missing Header")


def progress_bar(done, max):
    percent = float(done) / max
    width = 80
    done_width = int(width * percent) - 1
    rest_width = width - done_width - 1
    sys.stdout.write("\033[2K")
    sys.stdout.write("\r[{:s}{:s}] {:d}% {:d}/{:d}".format("*" * done_width,
                                                           " " * rest_width,
                                                           int(percent * 100), done, max,
                                                           done_width=done_width,
                                                           rest_width=rest_width))
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