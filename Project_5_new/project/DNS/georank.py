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


#FALSE_DISTANCE is in case that geolocation is not working correctly
FALSE_DISTANCE={
        '52.90.80.45': 10000000,
        '54.183.23.203': 10000000,
        '54.70.111.57': 10000000,
        '52.215.87.82':10000000,
        '52.28.249.79':10000000,
        '54.169.10.54':10000000,
        '52.62.198.57':10000000,
        '52.192.64.163':10000000,
        '54.233.152.60': 100000000
}


#The url of IPInfoDB's api
API='http://ipinfo.io/'
API_LOC='/loc'


def get_distances(client_ip):
    '''
    :param client_ip: client's ip address
    :return: its distances to all the EC2
    '''
    try:
        IPInfoDB_response=urllib2.urlopen(API+client_ip+API_LOC)
        response_details = ((IPInfoDB_response.read())[:-1]).split(',')
        latitude = float(response_details[0])
        longitude = float(response_details[1])
    except:
        print ("Something is wrong with Geolocation query")
        return FALSE_DISTANCE

    current_location=(latitude,longitude)
    result={}
    for ip in MAP:
        result[ip]=cal_distance(current_location,MAP[ip])
    #print result  #to sort a map: sorted(map.items(),key=lambda x:x[1])
    return result


def cal_distance(pointA,pointB):
    '''

    :param pointA: latitude and longitude of point A
    :param pointB: latitude and longitude of point B
    :return: distance between these two points
    '''
    return math.sqrt(reduce(lambda x, y: x + y,
                                map(lambda x, y: math.pow((x - y), 2), pointA, pointB), 0))



'''
def main():
    result_map=get_distances("178.137.38.15")
    print sorted(result_map.items(),key=lambda x:x[1])[0][0]

if __name__=='__main__':
    main()
'''