import re
import argparse

from MyCurl import MyCurl


class HTTP_STATUS:
    OK='200'
    MOVE_PERMANENTLY='301'
    FOUND='302'
    FORBIDDEN='403'
    NOT_FOUND='404'
    SERVER_ERROR='500'




class Crawler:


    LOG_IN_PAGE="/accounts/login/?next=/fakebook/"




    def __init__(self):
        self.frontier = set()
        self.flags = set()
        self.dest = ("cs5700sp17.ccs.neu.edu",80)
        self.curl = MyCurl(self.dest)

    def filterLinks(self, links):
        filteredLinks = set()
        for link in links:
            if link not in filteredLinks and not self.curl.is_visited_or_Not(link):
                filteredLinks.add(link)
        return filteredLinks

    def findLinks(self, body):
        pattern = re.compile(r'<a href=\"(/fakebook/[a-z0-9/]+)\">')
        links = pattern.findall(body)
        # Find a new url(have not been visited or found), then add it to urls
        return self.filterLinks(links)

    def findFlags(self, body):
        flags = re.findall(r'FLAG: (\w*)', body, re.I)
        return flags


    def login(self, username, password):
        form = "username=" + username + "&password=" + password
        self.curl.get(Crawler.LOG_IN_PAGE)
        csrf_token = self.curl.get_cookie('csrftoken')
        form += ("&csrfmiddlewaretoken=" + csrf_token)
        # ToDo:probably useless
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        loginResponse = self.curl.post(Crawler.LOG_IN_PAGE, headers, str(form))
        self.response_processor(Crawler.LOG_IN_PAGE, loginResponse)

    def response_processor(self, URL, response):
        #status code=200
        if response.status_code == HTTP_STATUS.OK:
            self.body_processor(response)

        #status code=403 or 404
        #if response.status_code == HTTP_STATUS.FORBIDDEN or response.status_code == HTTP_STATUS.NOT_FOUND:

        #status code=301 or 302
        if response.status_code ==  HTTP_STATUS.FOUND or response.status_code == HTTP_STATUS.MOVE_PERMANENTLY:
            forward_link=response.getHeader("location")
            if forward_link not in self.frontier and not self.curl.is_visited_or_Not(forward_link):
                self.frontier.add(forward_link)

        #status code=500
        if response.status_code ==  HTTP_STATUS.SERVER_ERROR:
            if URL not in self.frontier and not self.curl.is_visited_or_Not(URL):
                self.frontier.add(URL)


    def body_processor(self,response):
        response_body=response.body
        all_links=self.findLinks(response_body)
        all_flags=self.findFlags(response_body)
        for link in all_links:
            self.frontier.add(link)
        for flag in all_flags:
            self.flags.add(flag)


    def crawl(self,username,password):
        self.login(username,password)
        while len(self.frontier)>0 and len(self.flags)<5 :
            url=self.frontier.pop()
            response=self.curl.get(url)
            self.response_processor(url,response)




def main(args):
    mycrawler=Crawler()
    mycrawler.crawl(args.username,args.password)
    print("\n".join(mycrawler.flags))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='Process Input')
    parser.add_argument("username",help="username of fakebook")
    parser.add_argument("password",help="password of fakebook")
    args=parser.parse_args()
    main(args)






