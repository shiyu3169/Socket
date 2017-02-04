__author__="Zhongxi Wang"

import re


PATTERN=re.compile("(.*?)=(.*?);")

class CookieJar:

    def __init__(self):
        '''The jar is a cache to store cookies(key, value pairs)'''
        self.jar={}

    def add_cookie(self,key,value):
        self.jar[key]=value


    # ToDo: Use @dispatch to realize overloading here
    def add_cookie_from_string(self,str):
        matchPattern=PATTERN.search(str)
        if matchPattern:
            key=matchPattern.group(1)
            value=matchPattern.group(2)
            self.add_cookie(key,value)


    def get_cookie(self,key):
        return self.jar[key]

    def delete_cookie(self,key):
        del self.jar[key]

    def change_cookie(self,key,newValue):
        self.jar[key]=newValue


    def getAll(self):
        return self.jar

    def __str__(self):
        return ";".join(["{}={}".format(cookie.key, cookie.value) for cookie in self.jar])
