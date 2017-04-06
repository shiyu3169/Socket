#!/usr/bin/python
import argparse
import urllib2
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import shelve
import httplib
import logging

logging.basicConfig(level=logging.DEBUG)



class Cache:
    # The class to measure and handle cache in EC2
    def __init__(self):
        # Open -- file may get suffix added by low-level
        self.cache = shelve.open("cache")
        # Record of last time use for each path
        self.last_time_use = {}
        # Size of the cache
        self.size = 0

        # Update size based on cache data
        for key in self.cache.keys():
            self.last_time_use[key] = datetime.now()
            self.size += len(key) + len(self.cache[key])

    def store(self, key, value):
        # Store origin data to replicated server
        size = self.size + len(value) + len(key)
        # Max size of the replicated server
        max_size = 2 ** 20 * 10
        print "size: " + str(size)
        if size > max_size:
            # Add enough space for given key and value
            ordered_times = sorted(self.last_time_use, key=self.last_time_use.get)
            size = self.size + len(value) + len(key)
            while size > max_size and len(ordered_times) > 0:
                removed_key = ordered_times.pop()
                removed_value = self.cache[removed_key]
                self.size -= (len(removed_key) + len(removed_value))
                print "Cache is full"
                print removed_key + " is deleted"
                del self.cache[removed_key]
                del self.last_time_use[removed_key]
        self.last_time_use[key] = datetime.now()
        self.size += (len(value) + len(key))
        self.cache[key] = value

        # empty the cache and synchronize the persistent dictionary on disk
        self.cache.sync()


CACHE = Cache()


class Handler(BaseHTTPRequestHandler):

    def log_message(self, format,*args):
        """
        Kill the default logger.
        """
        return

    # The handler to handle request to server and give response
    def do_GET(self):
        # Function to handle get request
        if CACHE.cache.has_key(self.path):
            # If the replicated server has data
            CACHE.last_time_use[self.path] = datetime.now()
            data = CACHE.cache[self.path]
            response_code = 200
            self.reply(response_code, data)
        else:
            # Get data from origin server
            try:
                response_code, headers, data = self.get_from_origin()
            except urllib2.HTTPError as e:
                response_code, headers, data = e.getcode(), [], b""
            self.store(response_code, data)

    def get_from_origin(self):

        origin = args.origin

        conn = httplib.HTTPConnection(origin, 8080)
        conn.debuglevel = 1
        conn.request("GET", self.path, headers={'User-Agent': 'Python httplib'})
        reply = conn.getresponse()
        if reply.status == 200:
            print "Status OK"
            content = reply.read()
            self.send_response(200)
            # self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(content)
            return reply.status, [], content
        elif reply.status == 302 or reply.status == 301:
            print "Redirecting"
            temp = origin + ':8080'
            redirect = reply.getheader('location').split(temp)[-1]
            conn = httplib.HTTPConnection(origin, 8080)
            conn.request("GET", redirect, headers={'User-Agent': 'Python httplib'})
            reply = conn.getresponse()
            self.send_response(200)
            self.end_headers()
            content = reply.read()
            self.wfile.write(content)
            return reply.status, [], content
        else:
            print "Error"
            content = reply.read()
            self.send_response(reply.status)
            self.end_headers()
            self.wfile.write(content)
            return reply.status, [], content

    def store(self, respnse_code, message):
        # Store data to replicated server
        if respnse_code == 200:
            print "Saving to Cache"
            CACHE.store(self.path, message)

    def reply(self, response_code, data):
        # Reply response to the client
        self.send_response(response_code)
        self.end_headers()
        self.wfile.write(data)


def main():
    # Main function to start the server
    server = HTTPServer(('', args.port), Handler)

    server.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Read port from input
    parser.add_argument('-p', dest = 'port', type = int, required = True)
    # Read Origin from input
    parser.add_argument('-o', dest = 'origin', type = str, required = True)
    args = parser.parse_args()
    main()