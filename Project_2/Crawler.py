import re
import MyCurl


class Crawler:
    def __init__(self):
        self.frontier = set()
        self.flags = set()
        self.dest = ("cs5700sp17.ccs.neu.edu",80)
        self.curl = MyCurl(self.dest)

    def findLinks(self, body):
        pattern = re.compile(r'<a href=\"(/fakebook/[a-z0-9/]+)\">')
        links = pattern.findall(body)
        # Find a new url(have not been visited or found), then add it to urls
        return links

    def findFlags(self, body):
        pattern = re.compile(r"<h2 class='secret_flag' style=\\")
        flags = pattern.findall(body)
        return flags

    def filterLinks(self, links):
        for link in links:
            if link not in links and not self.curl.is_visited_or_Not(link):
                self.frontier.add(link)

    def login(self, username, password):
        self.curl.