__author__="Zhongxi Wang"

from ClientMessage import ClientMessage
from ServerMessage import ServerMessage
import socket
from CookieJar import CookieJar
from UrlEncodedForm import UrlEncodedForm
#import urllib

class MyCurl:

    def __init__(self,dest):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(dest)
        self.history=set()
        self.cookieJar=CookieJar()


    def request(self,method, URL, headers=None, body="" ):
        message=ClientMessage(method,URL,headers,body)
        #message.headers['Cookie']=str(self.cookieJar)
        self.history.add(URL)
        print(str(message))
        self.socket.sendall(str(message).encode())
        response=ServerMessage(self.socket)
        self.add_new_cookies(response)
        return response


    def get(self,URL,headers={}):
            return self.request("GET",URL,headers)


    def post(self,URL,headers={},body=""):
            return self.request("POST",URL,headers,body)


    def add_new_cookies(self,message):
        jar =message.cookieJar.getAll()
        for key in jar:
            self.cookieJar.add_cookie(key,jar[key])

    def is_visited_or_Not(self,link):
        return link in self.history

if __name__=="__main__":
    #test1 works so far
    '''
    Destination1=("cs5700sp17.ccs.neu.edu",80)
    test1=MyCurl(Destination1)
    test1.get("http://cs5700sp17.ccs.neu.edu/")
    '''
    #test2
    Destination2=("cs5700sp17.ccs.neu.edu",80)
    test2=MyCurl(Destination2)
    test2.get("/accounts/login/?next=/fakebook/")


    csrf_token=test2.cookieJar.get_cookie('csrftoken')
    form=UrlEncodedForm({"username":"001156814","password":"DVO8KW2F", "csrfmiddlewaretoken":csrf_token})
    headers= {
            "content-type": "application/x-www-form-urlencoded"
    }
    loginResponse=test2.post("/accounts/login/?next=/fakebook/",headers,str(form))
    print(loginResponse)
