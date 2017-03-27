#! /usr/bin/python3

import re


PATTERN=re.compile("(.*?)=(.*?);")

class CookieJar:
    """this class is used to handle cookies"""

    def __init__(self):
        '''The jar is a cache to store cookies(key, value pairs)'''
        self.jar={}


    def add_cookie(self,key,value):
        """add cookies into jar by given key"""
        self.jar[key]=value


    def add_cookie_from_string(self,str):
        matchPattern=PATTERN.search(str)
        if matchPattern:
            key=matchPattern.group(1)
            value=matchPattern.group(2)
            self.add_cookie(key,value)


    def get_cookie(self,key):
        """get cookie by given key"""
        return self.jar[key]

    def delete_cookie(self,key):
        """delete cookie by given key"""
        del self.jar[key]

    def change_cookie(self,key,newValue):
        """change cookie by given key"""
        self.jar[key]=newValue


    def getAll(self):
        """get all the cookies"""
        return self.jar

    def __str__(self):
        """transfer cookie jar into string for myCurl"""
        return ";".join(["{}={}".format(key, self.jar[key]) for key in self.jar])
