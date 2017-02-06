
__author__="Shiyu Wang"

from CookieJar import CookieJar


class ServerMessage:
    """this is a model that parsing received message from HTTP server"""

    def __init__(self, mySocket):
        """initialize the varaibles"""
        self.version = ""
        self.headers = {}
        self.body = ""
        self.status_code = None
        self.status = ""
        self.cookieJar = CookieJar()

        # Start reading received message and update variables
        socketFile = mySocket.makefile("rb")
        self.getStatus(socketFile)
        self.readHeader(socketFile)
        if "transfer-encoding" in self.headers and self.getHeader("transfer-encoding") == "chunked":
            self.readChunkedBody(socketFile)
        else:
            bodyLength = int(self.getHeader("content-length"))
            self.readBody(socketFile, bodyLength)
        socketFile.close()

    def getStatus(self, file):
        """read the first line to get status info"""
        statusLine = file.readline().decode("utf-8").strip()

        # check if the file is empty, raise exception
        if statusLine == "":
            raise Exception("socket is empty")

        version, status_code, status = statusLine.split(None, 2)
        self.version = str(version)
        self.status_code = str(status_code)
        self.status = str(status)

    def readHeader(self, file):
        """start reading the 2nd line of header"""

        key = ""
        while True:
            line = file.readline().decode("utf-8")
            # valid header line is supposed to always have ":" symbol
            if ":" not in line:
                break
            #remove leading space
            sLine = str(line.strip())

            if line[0] is " ":
                #self.addHeader(str(key.lower()), str(sLine))
                if str(key.lower()) == "set-cookie":
                    self.cookieJar.add_cookie_from_string(str(sLine))
                self.headers[str(key.lower())] = str(sLine)
                continue
            try:
                key, value = sLine.split(":", 1)
            except:
                raise Exception("invalid format of header")

            #self.addHeader(str(key.lower()), str(value.strip()))
            if str(key.lower()) == "set-cookie":
                self.cookieJar.add_cookie_from_string(str(value.strip()))
            self.headers[str(key.lower())] = str(value.strip())



    def readBody(self, file, fileLength):
        """read the body part of the message"""
        body = ""
        while fileLength > 0:
            data = file.read(fileLength).decode("utf-8")

            # check if the socket is empty
            if data is None:
                raise Exception("socket is empty")
            fileLength -= len(data)
            body += data
        self.body = body



    def readChunkedBody(self, file):
        """read the special chunked body of the message"""
        body= ""
        while 1:
            hexsize = file.readline().decode("utf-8")

            # check if the socket is empty
            if hexsize is None:
                raise Exception("empty socket")
            size = int(hexsize, 16)
            if size == 0:
                break
            data = ""
            while size > 0:
                line = file.read(size).decode("utf-8")
                size -= len(line)
                data += line
            body += data
            file.read(2)

        self.body = body
        self.readHeader(file)

    def getHeader(self, key):
        """get the header by given key"""
        if key not in self.headers:
            raise Exception("No such key in the header")
        else:
            return self.headers[key]







