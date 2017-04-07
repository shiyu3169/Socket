import urllib2
import math

# The IP addresses of EC2 servers, and their geolocations
MAP={
         '52.90.80.45':(39.0437,-77.4875),
        '54.183.23.203':(37.7749,-122.419),
        '54.70.111.57':(45.5234,-122.676),
        '52.215.87.82':(53.344,-6.26719),
        '52.28.249.79':(50.1155,8.68417),
        '54.169.10.54':(1.28967,103.85),
        '52.62.198.57':(-33.8679,151.207),
        '52.192.64.163':(35.6895,139.692),
        '54.233.152.60':(-23.5475,-46.6361)
}


#The KEY for IPInfoDB
KEY="6333a667b572041337caf64377744b660cd47a49eb668eff5858f826231b7e70"

#The url of IPInfoDB's api

api="http://api.ipinfodb.com/v3/ip-city/?key="+KEY+"&ip="



def get_distances(client_ip):
    IPInfoDB_response=urllib2.urlopen(api+client_ip)
    response_details=IPInfoDB_response.read().split(";")
    latitude=float(response_details[8])
    longitude=float(response_details[9])
    current_location=(latitude,longitude)
    result={}
    for ip in MAP:
        result[ip]=cal_distance(current_location,MAP[ip])
    print result



def cal_distance(pointA,pointB):
    return math.sqrt(reduce(lambda x, y: x + y,
                                map(lambda x, y: math.pow((x - y), 2), pointA, pointB), 0))


def main():
    get_distances("178.137.38.15")

if __name__=='__main__':
    main()