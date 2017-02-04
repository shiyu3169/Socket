__author__="Zhongxi Wang"

import re


PATTERN=re.compile("(.?)=(.?);")

class CookieJar:

    def __init__(self):
        '''The jar is a cache to store cookies(key, value pairs)'''
        self.jar={}

    def add_cookie(self,key,value):
        self.jar[key]=value


    # ToDo: Use @dispatch to realize overloading here
    def add_cookie_from_string(self,str):
        if PATTERN.search(str):
            self.add_cookie(PATTERN.group(1),PATTERN.group(2))


    def retrieve_cookie(self,key):
        return self.jar[key]

    def delete_cookie(self,key):
        del self.jar[key]

    def change_cookie(self,key,newValue):
        self.jar[key]=newValue

    def __iter__(self):
        for key in self.jar:
            yield self.cache[key]

    def __str__(self):
        return ";".join(["{}={}".format(cookie.key, cookie.value) for cookie in self.jar])
