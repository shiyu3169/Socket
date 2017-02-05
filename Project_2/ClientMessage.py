class ClientMessage:

    HTTP_VERSION="HTTP/1.1"

    HTTP_HEADERS={
        "Host": "cs5700sp17.ccs.neu.edu"
    }

    def __init__(self, method, URL, headers, body=""):
        """ Init the variables of the client message """
        self.method=method
        self.URL=URL
        self.body=body
        self.version=ClientMessage.HTTP_VERSION
        self.headers=ClientMessage.HTTP_HEADERS.copy()
        self.headers.update(headers)
        self.headers["Content-length"]=len(body)

    def __str__(self):
        """Transfer the message into string to send to server"""
        firstLine="{} {} {}".format(self.method,self.URL,self.version)

        headers=[]
        for key in self.headers:
            headers.append("{}:{}".format(key,self.headers[key]));

        headersLines="\n".join(headers)

        result="\n".join([firstLine,headersLines,"",self.body])+"\n"

        return result






