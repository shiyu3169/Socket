__author__="Zhongxi Wang"

from ClientMessage import ClientMessage
from ServerMessage import ServerMessage
import socket
from CookieJar import CookieJar

class MyCurl:

    def __init__(self,dest):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(dest)
        self.history=set()
        self.cookieJar=CookieJar()


    def request(self,method, URL, headers=None, body="" ):
        message=ClientMessage(method,URL,headers,body)
        message.headers['Cookie']=str(self.cookieJar)
        self.history.add(URL)
        self.socket.sendall(str(message).encode())
        response=ServerMessage(self.socket)
        self.add_new_cookies(response)
        return response


    def get(self,URL,headers={}):
            return self.request("GET",URL,headers)


    def post(self,URL,body=None, headers={}):
            return self.request("POST",URL,headers)


    def add_new_cookies(self,message):
        for cookie in message.CookieJar:
            self.cookieJar.add_cookie(cookie)

    def is_visited_or_Not(self,link):
        return link in self.history



if __name__=="__main__":
    Destination=("cs5700sp17.ccs.neu.edu",80)
    test=MyCurl(Destination)
    test.get("http://cs5700sp17.ccs.neu.edu/")