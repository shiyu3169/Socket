
class CookieJar:
    def __init__(self):
        '''The jar is a cache to store cookies(key, value pairs)'''
        self.jar={}

    def add_cookie(self,key,value):
        self.jar[key]=value


    # ToDo: Use @dispatch to realize overloading here
    def add_cookie_from_string(self,str):


    def retrieve_cookie(self,key):
        return self.jar[key]

    def delete_cookie(self,key):
        del self.jar[key]

    def change_cookie(self,key,newValue):