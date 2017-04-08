#!/usr/bin/python

import errno
import os
import signal
import socket
import datetime
import argparse
import urllib2
import shelve
import httplib
from datetime import datetime
import logging

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


class Cache:
    # The class to measure and handle cache in EC2
    def __init__(self):
        # Open -- file may get suffix added by low-level
        self.space = shelve.open("cache")
        # Record of last time use for each path
        self.last_time_use = {}
        # Size of the cache
        self.size = 0

        # Update size based on cache data
        self.size = os.stat('cache').st_size

    def store(self, key, value):
        # Store origin data to replicated server
        size = self.size + len(value) + len(key)
        # Max size of the replicated server
        max_size = 2 ** 20 * 9
        if size > max_size:
            # Add enough space for given key and value
            ordered_times = sorted(self.last_time_use, key=self.last_time_use.get)
            size = self.size + len(value) + len(key)
            while size > max_size and len(ordered_times) > 0:
                removed_key = ordered_times.pop()
                removed_value = self.space[removed_key]
                self.size -= (len(removed_key) + len(removed_value))
                print "Cache is full"
                print removed_key + " is deleted"
                del self.space[removed_key]
                del self.last_time_use[removed_key]
        self.last_time_use[key] = datetime.now()
        self.size += (len(value) + len(key))
        self.space[key] = value
        # empty the cache and synchronize the persistent dictionary on disk
        self.space.sync()


class Server:
    # The server class to handle http request and response
    def __init__(self):
        self.host = ""
        self.port = args.port
        self.origin = args.origin
        self.cache = Cache()
        self.server_address = (self.host, self.port)
        self.request_queue_size = 1024
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Return headers set by Web framework/Web application
        self.headers = []

    def do_GET(self):
        # Function to handle get request
        if self.cache.space.has_key(self.path):
            # If the replicated server has data
            self.cache.last_time_use[self.path] = datetime.now()
            data = self.cache.space[self.path]
            self.reply(data)
        else:
            # Get data from origin server
            try:
                response_code, headers, data = self.get_from_origin()
            except urllib2.HTTPError as e:
                response_code, headers, data = e.getcode(), [], b""
            self.store(response_code, data)

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
            print "Error Page"
            content = reply.read()
            self.reply(content)
            return reply.status, [], content

    def store(self, respnse_code, message):
        # Store data to replicated server
        if respnse_code == 200:
            self.cache.store(self.path, message)

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
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Read port from input
    parser.add_argument('-p', dest = 'port', type = int, required = True)
    # Read Origin from input
    parser.add_argument('-o', dest = 'origin', type = str, required = True)
    args = parser.parse_args()
    main()
