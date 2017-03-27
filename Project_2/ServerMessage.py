
__author__="Shiyu Wang"

from CookieJar import CookieJar


class ServerMessage:
    """this is a model that parsing received message from HTTP server"""

    def __init__(self, mySocket):
        """initialize the variables"""
        self.version = ""
        self.status_code = None
        self.status = ""
        self.cookieJar = CookieJar()
        self.headers = {}
        self.body = ""

        # Start reading received message and update variables
        socketFile = SocketReader(mySocket)
        self.getStatus(socketFile)
        self.readHeader(socketFile)
        if "transfer-encoding" in self.headers and self.getHeader("transfer-encoding") == "chunked":
            self.readChunkedBody(socketFile)
        else:
            bodyLength = int(self.getHeader("content-length"))
            self.readBody(socketFile, bodyLength)
        try:
            socketFile.close()
        except:
            raise Exception("Cannot close file stream from socket correctly")



    def getStatus(self, file):
        """read the first line to get status info"""
        try:
            statusLine = file.readline().decode("utf-8").strip()
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
            raise Exception ("Status line of response message is problematic")

    def readHeader(self, file):
        """start reading the 2nd line of header"""

        key = ""
        while 1:
            try:
                line = file.readline().decode("utf-8")
            except:
                raise Exception("Error in reading line")

            if line is None:
                raise Exception("Error read line")
            elif ":" not in line:
                # valid header line is supposed to always have ":" symbol
                break

            #remove leading space
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



    def readBody(self, file, fileLength):
        """read the body part of the message"""
        self.body=b""
        read = 0
        progress_bar(read, fileLength)
        while 1:
            try:
                data = file.read(fileLength)
            except:
                raise Exception("Error reading a line in the body")
            # check if the socket is empty
            if data is None:
                raise Exception("socket is empty")
            self.body += data
            fileLength -= len(data)
            progress_bar(read, fileLength)
            sys.stdout.write("\n")
            if num_read >= size:
                break




    def readChunkedBody(self, file):
        """read the special chunked body of the message"""
        print("Reading Chunked message, No file length")
        self.body= b""
        while 1:
            try:
                hexsize = file.readline().decode("utf-8")
            except:
                raise Exception("Error reading a line in chunked body")
            # check if the socket is empty
            if hexsize is None:
                raise Exception("empty socket")
            size = int(hexsize, 16)
            if size == 0:
                break
            data = ""
            while 1:
                try:
                    line = file.read(size).decode("utf-8")
                except:
                    raise Exception("Error reading a line in chunked body")
                data += line
                size -= len(line)
                if size<=0:
                    break
            self.body += data
            file.read(2)
        self.readHeader(file)

    def getHeader(self, key):
        """get the header by given key"""
        if key not in self.headers:
            raise Exception("No such key in the header")
        else:
            return self.headers[key]

