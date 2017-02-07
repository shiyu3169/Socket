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
        try:
            self.headers["Content-length"]=len(body)
        except:
            raise ("No field called Content-length in client message")

    def __str__(self):
        """Transfer the message into string to send to server"""
        firstLine=""+str(self.method)+" "+str(self.URL)+" "+str(self.version)

        headers=[]
        for key in self.headers:
            new_header_line=""+str(key)+":"+str(self.headers[key])
            headers.append(new_header_line)

        headersLines="\n".join(headers)

        result="\n".join([firstLine,headersLines,"",self.body])

        result+="\n"

        return result






