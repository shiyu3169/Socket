class SocketReader:
    """
    This class is designed to assist reading from sockets.
    It wraps the class and allows you to read by line or like normal.
    """
    def __init__(self, socket):
        """
        Initialize
        :param socket: The socket to read from
        """
        self.socket = socket

    def readline(self):
        """
        Assuming that the data is text, read characters until we encounter a newline.
        :return:
        """
        line = b""
        c = None
        while c != b"\n":
            c = self.socket.recv(1)
            line += c
        return line

    def read(self, max):
        """
        Basically a normal receive.  Get max bytes or fewer.
        :param max: The max number of bytes to read.
        :return: The bytes read from the socket.
        """
        return self.socket.recv(max)