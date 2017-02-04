from CookieJar import CookieJar
import socket


class ServerMessage:
    """this is a model that parsing received message from HTTP server"""

    def __init__(self, mySocket):
        self.version = ""
        self.headers = {}
        self.body = ""
        self.status_code = None
        self.status = ""
        self.cookieJar = CookieJar()

        socketFile = mySocket.makefile("rb")
        self.readHeader(socketFile)
        bodyLength = int(self.getHeader("content-length"))
        self.readBody(socketFile, bodyLength)
        socketFile.close()

    def readHeader(self, file):
        # read the first line to get status info
        statusLine = file.readline().decode("utf-8").strip()
        version, status_code, status = statusLine.split(None,2)
        self.version = str(version)
        self.status_code = str(status_code)
        self.status = str(status)

        #start reading 2nd line of header
        key = ""

        while True:
            line = file.readline().decode("utf-8")

            if ":" not in line:
                break
            #remove leading space
            sLine = str(line.strip())

            #TODO: may be uselss
            if line[0] is " ":
                self.addHeader(str(key.lower()), str(sLine))
                continue
            key, value = sLine.split(":", 1)

            self.addHeader(str(key.lower()), str(value.strip()))

    def addHeader(self, key, value):

        if key == "set-cookie":
            self.cookieJar.add_cookie_from_string(value)

        #TODO: maybe useless
        if key in self.headers.keys():
            self.headers[key] = str(self.headers[key]) +", " + str(value)
        else:
            self.headers[key] = str(value)

    def readBody(self, file, fileLength):
        body = ""
        #TODO: may be useless as well
        while fileLength > 0:
            data = file.read(fileLength).decode("utf-8")
            fileLength -= len(data)
            body += data
        self.body = body

    def readChunkedBody(self, file):
        body= ""
        while 1:
            hexsize = file.readline().decode("utf-8")
            size = int(hexsize, 16)
            if size == 0:
                break
            data = ""
            #TODO: maybe useless
            while size > 0:
                line = file.read(size).decode("utf-8")
                size -= len(line)
                data += line
            body += data
            file.read(2)

        self.body = body
        self._read_headers(file)

    def getHeader(self, key):
        if key not in self.headers:
            raise Exception
        else:
            return self.headers[key]







