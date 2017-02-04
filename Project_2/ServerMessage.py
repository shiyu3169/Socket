from CookieJar import CookieJar


class ServerMessage:
	"""
	this is a model that parsing received message from HTTP server
	"""

	def __init__(self, socket):
		self.version = ""
		self.headers = {}
		self.body = ""
		self.status_code = None
		self.status = ""
		self.cookieJar = CookieJar()
		#TODO: parse the received message

	def readHeader(self, file):
		# read the first line to get status info
		statusLine = file.readlline().decode("utf-8")

		version, status_code, status = statusLine.split()
		self.version = version
		self.status_code = status_code
		self.status = status

		#start reading 2nd line of header
		key = ""

		while(1):
			line = file.readline().decode("utf-8")

			# TODO: if head ends
			if ":" not in line:
				break

			#remove leading space
			sLine = line.strip()

			#TODO: may be uselss
			if line[0] is " ":
				self.addHeader(key.lower(), sLine)
				continue

			key, value = sLine.split(":", 1)
			self.addHeader(key.lower(), value)

	def addHeader(self, key, value):

		if key == "set-cookie":
			self.cookieJar.add_cookie_from_string



