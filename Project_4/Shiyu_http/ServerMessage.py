import logging
import sys

from http_browser.CookieJar import CookieJar
from http_browser.SocketReader import SocketReader


__author__ = 'njhazelh'

log = logging.getLogger("http")


class HTTP_STATUS:
    """
    This is basically an enum representing HTTP_STATUS codes from the server.
    """
    OK = 200
    MOVED_PERM = 301
    FOUND = 302
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500


class ServerMessage:
    """
    This is a model that encapsulates the parsing of messages from an HTTP server.
    """

    def __init__(self, sock):
        """
        Initialize this message and read the data from the network.
        This should probably be refactored somehow.
        :param sock: The socket to read this message from.
        """
        self.data = b""
        self.version = ""
        self.headers = {}
        self.body = b""
        self.status_code = None
        self.cookieJar = CookieJar()
        self._getMessage(sock)


    def _getMessage(self, sock):
        """
        Read the headers and body into this structure from the network.
        :param sock: A HttpSocket containing a server response
        """
        file = SocketReader(sock)
        self._read_status(file)
        self._read_headers(file)

        if self.safe_get_header("transfer-encoding") == "chunked":
            self._read_chunked(file)
        else:
            self._read_body(int(self.get_header("content-length")), file)

    def _read_status(self, file):
        """
        Read the status line from the message and set version, status_code, and reason.
        :param file: The file descriptor for the socket to read from.
        :except: BadStatusException The status line is malformed somehow.
        """
        status = file.readline()
        self.data += status
        status = status.decode()

        if not status:
            raise Exception("empty socket")
        try:
            version, status_code, status = status.strip().split(None, 2)
            self.version = version
            self.status_code = int(status_code)
            self.reason = status
        except ValueError:
            raise Exception("Bad status")

    def _read_headers(self, socket_reader):
        """
        Read the headers for this message.
        :param socket_reader: The file for the socket to read from.
        :except EmptySocketException: The socket has closed.
        :except BadHeaderException: A header is malformed somehow.
        """
        key = ""
        while True:
            line = socket_reader.readline()
            self.data += line

            if line is None:
                raise Exception("empty socket")

            line = line.decode()

            if ":" not in line:
                break

            stripped = line.strip()

            if line[0] is " ":
                self._add_header(key, stripped)
                continue

            try:
                key, value = stripped.split(": ", 1)
                self._add_header(key, value)
            except ValueError:
                raise Exception("Bad header")


    def _add_header(self, key, value):
        """
        Add a header to this model.  Combine with commas if key already exists.
        :param key: The header key
        :param value: The header value
        """
        key = key.lower()

        if key == "set-cookie":
            self.cookieJar.add_cookie_from_string(value)

        if key in self.headers.keys():
            current_val = self.headers[key]
            current_val = current_val + ", " + value
            self.headers[key] = current_val
        else:
            self.headers[key] = value

    def _read_body(self, size, socket_reader):
        """
        Read the body of the message. This should be done if the message
        has a body and the transfer-encoding header is not "chunked".
        :param size: The size of the body in bytes
        :param socket_reader: The file to read the body from.
        """
        data = b""
        num_read = 0
        progress_bar(num_read, size)
        while num_read < size:
            new_data = socket_reader.read(size)
            if new_data is None:
                raise Exception("empty socket")
            new_data = new_data
            num_read += len(new_data)
            data += new_data
            progress_bar(num_read, size)
        sys.stdout.write("\n")
        self.body = data
        self.data += data

    def _read_chunked(self, file):
        """
        Read a chunked body.  This should be called when the transfer-encoding of the
        message is "chunked"
        :param file: The file to read this from.
        """
        log.debug("Reading a chunked message")
        print("Reading Chunked message. Cannot predict length")
        body = b""
        while True:
            size_line = file.readline()
            if size_line is None:
                raise Exception("Empty Socket")
            size_line = size_line.decode("utf-8").strip()
            size = int(size_line, 16)
            if size == 0:
                break
            data = b""
            while size > 0:
                new_data = file.read(size)
                if new_data is None:
                    raise Exception("Empty Socket")
                new_data = new_data
                size -= len(new_data)
                data += new_data
            body += data
            file.read(2)  # read line \r\n
        self.body = body
        self._read_headers(file)


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

    def safe_get_header(self, key):
        """
        Get a header or return an empty string if it does not exist.
        :param key: The key of the header to get.  Should be lower-case
        :return: The header value or ""
        """
        if key in self.headers.keys():
            return self.get_header(key)
        else:
            return ""

    def __str__(self):
        """
        Convert this message back to a string.
        :return: A String representing this message.  It should almost match what was received,
        but the header keys will be lower case and headers with the same key will be combined
        into a comma separated list.
        """
        status = "{} {} {}".format(self.version, self.status_code, self.reason)
        headers = "\r\n".join(["{}: {}".format(key, self.headers[key]) for key in self.headers])
        return "\r\n".join([status, headers, "", self.body])


CLEAR_LINE = "\033[2K"

def progress_bar(done, max):
    percent = float(done) / max
    width = 80
    done_width = int(width * percent) - 1
    rest_width = width - done_width - 1
    sys.stdout.write(CLEAR_LINE)
    sys.stdout.write("\r[{:s}>{:s}] {:d}% {:d}/{:d}".format("=" * done_width,
                                                           " " * rest_width,
                                                           int(percent * 100), done, max,
                                                           done_width=done_width,
                                                           rest_width=rest_width))
