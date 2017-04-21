import httplib
import zlib
import Queue
from threading import Thread


origin = "ec2-54-166-234-74.compute-1.amazonaws.com"
port = 8080
web_names = Queue.Queue()

def build_queue():
    # Download and compress based on pathname
    f = open('pathname', 'rb')
    line = f.readline()
    while line != "":
        name = line.strip()
        web_names.put(name)
        line = f.readline()


def download(name):
    conn = httplib.HTTPConnection(origin, port)
    conn.debuglevel = 1
    conn.request("GET", '/wiki/' + name, headers={'User-Agent': 'Python httplib'})
    reply = conn.getresponse()
    if reply.status != 300 or reply.status != 301:
        content = reply.read()
    return content


def compress(name):
    str_object2 = zlib.compress(download(name), 9)
    f = open('./zip/' + name + '.Z', 'wb')
    f.write(str_object2)
    f.close()


def compress_forever():
    while not web_names.empty():
        compress(web_names.get())


def threaded_function(num_threads):
    for i in range(num_threads):
        worker = Thread(target=compress_forever)
        worker.setDaemon(True)
        worker.start()
    worker.join()


def main():
    # build a queue of names
    build_queue()
    threaded_function(10)


if __name__=="__main__":
    main()
