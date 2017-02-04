class ClientMessage:

    #ToDo: This one may be useless
    HTTP_VERSION="HTTP/1.1"

    #ToDo: This one may be useless as well
    HTTP_HEADERS={
        "Host": "cs5700sp17.ccs.neu.edu",
        "User-Agent":"FailSauce/0.1"
    }


    def __init__(self, method, URL, headers, body=""):
        self.method=method
        self.URL=URL
        self.body=body
        self.version=self.HTTP_VERSION
        self.headers=self.HTTP_HEADERS
        self.headers.update(headers)

        #ToDo:This one may be useless
        self.headers["Content-length"]=len(body)

    def __str__(self):

        firstLine="{} {} {}".format(self.method,self.URL,self.version)

        headers=[]
        for key in self.headers:
            headers.append("{}:{}".format(key,self.headers[key]));

        headersLines="\n".join(headers)

        result="\n".join([firstLine,headersLines,self.body])+"\n"

        return result






