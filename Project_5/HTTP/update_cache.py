import httplib
import zlib

# Add disk files' names into set

origin = "ec2-54-166-234-74.compute-1.amazonaws.com"
port = 8080


def download(name):
    conn = httplib.HTTPConnection(origin, port)
    conn.debuglevel = 1
    conn.request("GET", '/wiki/' + name, headers={'User-Agent': 'Python httplib'})
    reply = conn.getresponse()
    if reply.status != 300 or reply.status != 301:
        content = reply.read()
    return content


def compress(file, name):
    str_object2 = zlib.compress(file, 9)
    f = open('./zip/' + name + '.Z', 'wb')
    f.write(str_object2)
    f.close()


def main():
    f = open('pathname', 'rb')
    line = f.readline()
    while line != "":
        name = line.strip()
        compress(download(name), name)
        line = f.readline()
    return

if __name__=="__main__":
    main()