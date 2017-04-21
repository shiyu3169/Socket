#!/usr/bin/python

import errno
import os
import signal
import socket
import argparse
import urllib2
import httplib
import zlib
import urllib
import threading
import Queue


def grim_reaper(signum, frame):
    # Handle zombies from child process
    while True:
        try:
            pid, status = os.waitpid(
                -1,  # Wait for any child process
                os.WNOHANG  # Do not block and return EWOULDBLOCK error
            )
        except OSError:
            return

        if pid == 0:  # no more zombies
            return


def add_pathname_to_queue(queue):
    # Put names in pathname2 into queue
    f = open('pathname2', 'rb')
    line = f.readline()

    while line != "":
        queue.put(line.strip())
        line = f.readline()
    f.close()


class Server:
    # The server class to handle http request and response
    def __init__(self):
        self.host = ""
        self.port = args.port
        self.origin = args.origin
        self.server_address = (self.host, self.port)
        self.request_queue_size = 1024
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Return headers set by Web framework/Web application
        self.headers = []
        self.path = ""
        self.disk_path_names = [] # Path name used to look for file on disk
        self.memory_path_to_file = {} # key = path name, value = file in memory
        self.queue = Queue.Queue()
        add_pathname_to_queue(self.queue)
        self.thread = threading.Thread(target=self.add_pages_to_memory)
        self.thread.setDaemon(True)

        # Add disk files' names into set
        f = open('pathname', 'rb')
        line = f.readline()
        while line != "":
            self.disk_path_names.append(line.strip())
            line = f.readline()
        f.close()

    def add_pages_to_memory(self):
        #save 299 pages into cache2
        while not self.queue.empty():
            path = self.queue.get()
            conn = httplib.HTTPConnection(self.origin, 8080)
            conn.debuglevel = 0
            conn.request("GET", "/wiki/" + path, headers={'User-Agent': 'Python httplib'})
            reply = conn.getresponse()
            response = zlib.compress(reply.read(), 9)
            self.memory_path_to_file[path] = response

    def do_GET(self):
        # Function to handle get request
        try:
            name = urllib.unquote(self.path.split('/')[-1])
            if name == "":
                name = "Main_Page"
            if name in self.disk_path_names:
                str_object1 = open('./zip/' + name + '.Z', 'rb').read()
                str_object2 = zlib.decompress(str_object1)
                self.reply(str_object2)
            elif name in self.memory_path_to_file:
                str_object1 = self.memory_path_to_file[name]
                str_object2 = zlib.decompress(str_object1)
                self.reply(str_object2)
            else:
                # Get data from origin server
                try:
                    response_code, headers, data = self.get_from_origin()
                except urllib2.HTTPError as e:
                    response_code, headers, data = e.getcode(), [], b""
        except:
            # Get data from origin server
            try:
                response_code, headers, data = self.get_from_origin()
            except urllib2.HTTPError as e:
                response_code, headers, data = e.getcode(), [], b""

    def reply(self, data):
        # Send response back
        result = self.parse_response(data)
        self.client_connection.sendall(result)

    def handel_request(self):
        # Hanle incoming request
        self.request_data = request_data = self.client_connection.recv(1024)
        self.parse_request(request_data)
        self.do_GET()

    def parse_response(self, result):
        # status, response_headers = self.headers
        response = 'HTTP/1.1 200 OK\n'
        response += '\n'
        for data in result:
            response += data
        return response

    def get_from_origin(self):
        # Get response from origin
        conn = httplib.HTTPConnection(self.origin, 8080)
        conn.debuglevel = 1
        conn.request("GET", self.path, headers={'User-Agent': 'Python httplib'})
        reply = conn.getresponse()
        if reply.status == 200:
            print "Status OK"
            content = reply.read()
            self.reply(content)
            return reply.status, [], content
        elif reply.status == 302 or reply.status == 301:
            print "Redirecting"
            temp = self.origin + ':8080'
            redirect = reply.getheader('location').split(temp)[-1]
            conn = httplib.HTTPConnection(self.origin, 8080)
            conn.request("GET", redirect, headers={'User-Agent': 'Python httplib'})
            reply = conn.getresponse()
            content = reply.read()
            self.reply(content)
            return reply.status, [], content
        else:
            content = reply.read()
            self.reply(content)
            return reply.status, [], content

    def parse_request(self, text):
        # Parse request to get path
        try:
            request_line = text.splitlines()[0]
            request_line = request_line.rstrip('\n')
            # Break down the request line into components
            (self.request_method,  # GET
             self.path,            # /path
             self.request_version  # HTTP/1.1
             ) = request_line.split()
        except:
            pass

    def serve_forever(self):
        # Start listening
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(self.server_address)
        self.listen_socket.listen(self.request_queue_size)
        print('Serving HTTP on port {port} ...'.format(port=self.port))

        signal.signal(signal.SIGCHLD, grim_reaper)

        while True:
            try:
                self.client_connection, client_address = self.listen_socket.accept()
            except IOError as e:
                code, msg = e.args
                # restart 'accept' if it was interrupted
                if code == errno.EINTR:
                    continue
                else:
                    raise

            pid = os.fork()
            if pid == 0:  # child
                self.listen_socket.close()  # close child copy
                self.handel_request()
                self.client_connection.close()
                os._exit(0)
            else:  # parent
                self.client_connection.close()  # close parent copy and loop over


def main():
    # Main function to start the server
    server = Server()
    server.thread.start()
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Read port from input
    parser.add_argument('-p', dest = 'port', type = int, required = True)
    # Read Origin from input
    parser.add_argument('-o', dest = 'origin', type = str, required = True)
    args = parser.parse_args()
    main()
