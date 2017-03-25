__author__="Zhongxi Wang"

from http_browser.ClientMessage import ClientMessage
from http_browser.ServerMessage import ServerMessage
from tcp.TCPSocket import TCPSocket
from http_browser.CookieJar import CookieJar

class MyCurl:
    """Curl to connect server and client"""
    def __init__(self,dest):
        try:
            self.socket = TCPSocket()
        except:
            raise Exception("Cannot initiate socket correctly")
        # self.socket.connect(dest)
        self.history=set()
        self.cookieJar=CookieJar()
        self.dest = dest

    def request(self,method, URL, headers=None, body=""):
        """sending request to server"""
        message=ClientMessage(method, URL, headers, body)
        message.headers['Cookie']=str(self.cookieJar)
        self.history.add(URL)
        # try:
        #     self.socket = TCPSocket()
        # except:
        #     raise Exception("Cannot initiate socket correctly")
        try:
            self.socket.connect(self.dest)
            self.socket.sendall(str(message).encode())
        except:
            raise Exception("connection failed")
        try:
            response=ServerMessage(self.socket)
        except:
            raise Exception("empty socket")
        self.add_new_cookies(response)
        # try:
        #     self.socket.close()
        # except:
        #     raise Exception("Socket cannot close correctly")
        return response


    def get(self,URL,headers={}):
        """sending get request"""
        return self.request("GET", URL, headers)

    def post(self,URL,headers={}, body=""):
        """sending post request"""
        return self.request("POST", URL, headers, body)


    def add_new_cookies(self,message):
        """add new coockies to the cookie jar"""
        jar =message.cookieJar.getAll()
        for key in jar:
            self.cookieJar.add_cookie(key, jar[key])

    def is_visited_or_Not(self, link):
        """check if the link has been visited"""
        return link in self.history

    def get_cookie(self, str):
        """get the cookie"""
        return self.cookieJar.get_cookie(str)

# Used to test Curl and lower level HTTP Protocol
if __name__=="__main__":
     #test1 works so far

     Destination1=("david.choffnes.com",80)
     test1=MyCurl(Destination1)
     response=test1.get("http://david.choffnes.com/classes/cs4700sp17/project4.php")
     file=open("test.html", 'wb')
     file.write(response.body)


     #test2
     Destination2=("cs5700sp17.ccs.neu.edu",80)
     test2=MyCurl(Destination2)
     response2=test2.get("/accounts/login/?next=/fakebook/")
     file2=open("test2.html", 'wb')
     file2.write(response2.body)


#     csrf_token=test2.cookieJar.get_cookie('csrftoken')
#     form="username=001156814&password=DVO8KW2F&csrfmiddlewaretoken="+csrf_token
#     headers= {
#             "content-type": "application/x-www-form-urlencoded"
#     }
#     loginResponse=test2.post("/accounts/login/?next=/fakebook/",headers,str(form))
#     print(loginResponse.headers)
#
#     print(test2.get("http://cs5700sp17.ccs.neu.edu/fakebook/").headers)
#
#     print(test2.get("/fakebook/294230082/").status_code)