import requests
import bs4
import json
from urllib.parse import urlencode, quote_plus, unquote, quote


station_api_key = 'KakaoAK 2923b1b707b4bddd84bbc07c7bb3f14a'
my_api_key = unquote('bhQZulxZSz%2FeMsDseMe2DSccTVB%2BQPnxTxDp4SrK7HYRP%2BS0YDiBn93FLz0d%2FMFbyMPUqAvaMqrtW4e9%2FnHYhA%3D%3D')

class StationGps:

    def get_near_station_gps(self, gps_x, gps_y):

        gps_x_list = []
        gps_y_list = []
        name_list = []
        distance = []

        url = 'https://dapi.kakao.com/v2/local/search/category.json'
        queryParams = '?' + urlencode({quote_plus('page'): '1',
                                       quote_plus('size'): '15',
                                       quote_plus('sort'): 'distance',
                                       quote_plus('category_group_code'): 'SW8',
                                       quote_plus('x'): gps_x,
                                       quote_plus('y'): gps_y,
                                       quote_plus('radius'): '400'})

        header = {'Authorization': station_api_key}
        response = requests.get(url, headers=header, params=queryParams)
        station_dict= json.loads(response.text)

        for vals_dict in station_dict['documents']:
            name_list.append(vals_dict['place_name'])
            distance.append(vals_dict['distance'])

        return name_list, distance

    def get_station_gps(self, station):

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
            if station == vals_dict['place_name']:
                gps_x = vals_dict['x']
                gps_y = vals_dict['y']

        return gps_x, gps_y



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

        for item_tag in itemList_tag:

            # 지하철 타고 환승 없이 가는 경로의 시간을 찾는 경우이므로 환승 횟수가 1인 경우를 검색
            pathList_tag = item_tag.find_all('pathList')

            if len(pathList_tag) == 1 :
                time = item_tag.find('time').text

        return time


class SubwayDestination:

    def __init__(self, gps_x, gps_y, time):

        self.gps_x = gps_x
        self.gps_y = gps_y
        self.time = time

    def result_sub_station(self):

        result_gps = []
        name_list = []
        distance = []
        result_station = []
        result_time = []
        cnt = 1
        tmp_time = 0

        stt_gps = StationGps()
        name_list, distance = stt_gps.get_near_station_gps(self.gps_x, self.gps_y)

        for i, distance in enumerate(distance):
            # 목적지에서 지하철역까지 거리를 성인 평균 보행 속도 67m/s 를 나누어 지하철역까지의 보행시간 계산
            self.time = self.time - int(distance)/67
            station_name = name_list[i].split()[0]
            station_route = name_list[i].split()[1]

            for j, sub in enumerate(subway_route):
                if station_name in sub and station_route == sub[0]:
                    #아래방향으로 지하철역 확인
                    while(True):
                        if j+cnt >= len(subway_route):
                            cnt = 1
                            tmp_time = 0
                            break
                        # 도착 지하철역 까지의 시간이 처음 입력된 시간을 초과하면 break
                        if tmp_time + int(subway_route[j+cnt][2]) > self.time:
                            if subway_route[j][0] == subway_route[j + cnt][0]:
                                # 같은 지하철 노선인지 확인 후 추가
                                result_station.append(subway_route[j+cnt][1] + ' ' + subway_route[j+cnt][0])
                                result_time.append(tmp_time)

                                # 도착 지하철역보다 가까운 곳 -5분까지 출력
                                while True:
                                    cnt -=1
                                    if tmp_time - int(subway_route[j+cnt][2]) > self.time - 5:
                                        tmp_time -= int(subway_route[j+cnt][2])

                                        if subway_route[j][0] == subway_route[j + cnt][0]:
                                            result_station.append(subway_route[j + cnt][1] + ' ' + subway_route[j + cnt][0])
                                            result_time.append(tmp_time)
                                    else:
                                        break
                            cnt = 1
                            tmp_time = 0
                            break
                        else:
                            tmp_time += int(subway_route[j+cnt][2])
                            cnt += 1


                    # 위방향으로 지하철역 확인
                    while (True):
                        if j-cnt < 0:
                            cnt = 1
                            tmp_time = 0
                            break
                        # 도착 지하철역 까지의 시간이 처음 입력된 시간을 초과하면 break
                        if tmp_time + int(subway_route[j-cnt+1][2]) > self.time:
                            if subway_route[j][0] == subway_route[j - cnt][0]:
                                # 같은 지하철 노선인지 확인 후 추가
                                result_station.append(subway_route[j-cnt][1] + ' ' + subway_route[j-cnt][0])
                                result_time.append(tmp_time)

                                # 도착 지하철역보다 가까운 곳 -5분까지 출력
                                while True:
                                    cnt -= 1
                                    if tmp_time - int(subway_route[j - cnt + 1][2]) > self.time - 5:
                                        tmp_time -= int(subway_route[j - cnt + 1][2])
                                        if subway_route[j][0] == subway_route[j - cnt][0]:
                                            result_station.append(subway_route[j - cnt][1] + ' ' + subway_route[j - cnt][0])
                                            result_time.append(tmp_time)
                                    else:
                                        break
                            cnt = 1
                            tmp_time = 0
                            break
                        else:
                            tmp_time += int(subway_route[j-cnt+1][2])
                            cnt += 1

        for stt in result_station:
            gps_x, gps_y = StationGps().get_station_gps(stt)
            result_gps.append([gps_x, gps_y])

        return  result_gps, result_station, result_time
