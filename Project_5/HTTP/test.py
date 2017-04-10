import _sqlite3
import httplib

key = "/wiki/Maximilian_Schell"

def get_from_origin():
    # Get response from origin
    conn = httplib.HTTPConnection("ec2-54-166-234-74.compute-1.amazonaws.com", 8080)
    conn.debuglevel = 0
    conn.request("GET", key, headers={'User-Agent': 'Python httplib'})
    reply = conn.getresponse()
    if reply.status != 301 or reply.status != 302:
        print "Status OK"
        content = reply.read()
        return content

value = get_from_origin()

conn = _sqlite3.connect('cache.db')
conn.text_factory = str
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS cache2
             (path TEXT, content TEXT)''')

c.execute("INSERT INTO cache2 VALUES (?, ?)", (key, value))
# c.execute("SELECT * FROM cache2")
#
# n= 0
# for row in c.execute('SELECT * FROM cache2'):
#         print row
#         n+=1
#
# print n
conn.commit()
conn.close()
