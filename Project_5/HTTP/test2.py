import _sqlite3
key = "/wiki/Deathlok"

conn = _sqlite3.connect('cache.db')
conn.text_factory = str
c = conn.cursor()
c.execute("DELETE FROM cache2 WHERE path=?", (key,))

# c.execute("SELECT * FROM cache2")
#
# for row in c.execute('SELECT * FROM cache2'):
#         print row

conn.commit()
conn.close()