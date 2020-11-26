import requests
import bs4
import json
import csv
from urllib.parse import urlencode, quote_plus, unquote, quote

station_api_key = 'KakaoAK 2923b1b707b4bddd84bbc07c7bb3f14a'
my_api_key = 'bhQZulxZSz%2FeMsDseMe2DSccTVB%2BQPnxTxDp4SrK7HYRP%2BS0YDiBn93FLz0d%2FMFbyMPUqAvaMqrtW4e9%2FnHYhA%3D%3D'

class StationGps:

    def get_near_station_gps(self, gps_x, gps_y):

        gps_x_list = []
        gps_y_list = []

        url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
        queryParams = '?' + urlencode({quote_plus('page'): '1',
                                       quote_plus('size'): '15',
                                       quote_plus('sort'): 'distance',
                                       quote_plus('category_group_code'): 'SW8',
                                       quote_plus('x'): gps_x,
                                       quote_plus('y'): gps_y,
                                       quote_plus('radius'): '1000',
                                       quote_plus('query'): 'station'})

        header = {'Authorization': station_api_key}
        response = requests.get(url, headers=header, params=queryParams)
        station_dict= json.loads(response.text)

        for vals_dict in station_dict['documents']:
            gps_x_list.append(vals_dict['x'])
            gps_y_list.append(vals_dict['y'])

        return gps_x_list, gps_y_list

    def get_station_gps(self, gps_x, gps_y, station):

        gps_x_list = []
        gps_y_list = []
        url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
        queryParams = '?' + urlencode({quote_plus('page'): '1',
                                       quote_plus('size'): '15',
                                       quote_plus('sort'): 'accuracy',
                                       quote_plus('category_group_code'): 'SW8',
                                       quote_plus('query'): station})

        header = {'Authorization': station_api_key}
        response = requests.get(url, headers=header, params=queryParams)
        station_dict = json.loads(response.text)

        for vals_dict in station_dict['documents']:
            gps_x_list.append(vals_dict['x'])
            gps_y_list.append(vals_dict['y'])

        return gps_x_list, gps_y_list



class SubwayPathData:

    def subway_path(self, start_x, start_y, end_x, end_y):

        url = 'http://ws.bus.go.kr/api/rest/pathinfo/getPathInfoBySubway'

        queryParams = '?' + urlencode({quote_plus('ServiceKey'): my_api_key,
                                       quote_plus('startX'): start_x,
                                       quote_plus('startY'): start_y,
                                       quote_plus('endX'): end_x,
                                       quote_plus('endY'): end_y})

        response = requests.get(url + queryParams).text.encode('utf-8')
        xmlobj = bs4.BeautifulSoup(response, 'lxml-xml')
        itemList_tag = xmlobj.findAll('itemList')

        for i in range(0,len(itemList_tag)):

            # 지하철 타고 환승 없이 가는 경로의 시간을 찾는 경우이므로 환승 횟수가 1인 경우를 검색
            pathList_tag = itemList_tag[i].find_all('pathList')

            if len(pathList_tag) == 1 :
                gps_x = itemList_tag[i].find('tx').text
                gps_y = itemList_tag[i].find('ty').text

        return gps_x, gps_y



if __name__ == '__main__':

    stt = StationGps()

    gps_x, gps_y = stt.get_near_station_gps(127.0816985, 37.5642135)

    print(gps_x)
    print(gps_y)

    sub_list = []

    with open('D:/서울교통공사 역간 거리 및 소요시간 정보.csv','r') as f:
        reader = csv.reader(f)

        for txt in reader:
            sub_list.append(txt)

    print(sub_list)
