#! /usr/bin/python3

import socket
from urllib.parse import urlparse
import argparse
from HTTP.MyCurl import MyCurl


HTTP_SOCKET=80


def main(args):
    domain,path,filename=parse_url(args.url)
    try:
        Destination = (domain, HTTP_SOCKET)
        conn = MyCurl(Destination)
        response = conn.get(path)
    except:
        raise Exception("Cannot connect")
    if response.status_code != '200':
        raise Exception("Connection fails")
    else:
        print("Saving response to %s" % (filename))
        file = open(filename,'wb')
        file.write(response.body)

def parse_url(url):
    '''
    :param url: the url to parse
    :return:
    '''
    if not url.startswith("http"):
        url="http://"+url
    parsed_url=urlparse(url)

    if parsed_url.netloc=='':
        raise Exception("No domain name")
    try:
        socket.gethostbyname(parsed_url.netloc)
    except Exception:
        raise Exception("Cannot find IP address for this url")

    domain=parsed_url.netloc

    filename=parsed_url.path.split("/")[-1]

    if filename=="":
        filename="index.html"

    return domain,url,filename


if __name__=="__main__":
    parser=argparse.ArgumentParser(description='Process Input')
    parser.add_argument("url",help="url for the file to download")
    args=parser.parse_args()
    main(args)



