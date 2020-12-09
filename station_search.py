import requests
import bs4
from urllib.parse import urlencode, quote_plus, unquote, quote
import pandas as pd
import seoulbus as sb
import seoulsubway as ssub


subway_route = pd.read_csv('subway_time.csv', encoding='CP949')

class SubwayPathData:

    def subway_path(self, start_x, start_y, end_x, end_y):

        url = 'http://ws.bus.go.kr/api/rest/pathinfo/getPathInfoBySubway'

        header = {'serviceKey':sb.read_key('kr.go.data.jsh')}

        params = dict()
        params['startX'] = start_x
        params['startY'] = start_y
        params['endX'] = end_x
        params['endY'] = end_y

        response = requests.get(url, params=params, headers=header)
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
        cnt = 1
        tmp_time = 0

        #stt_gps = StationGps()
        #name_list, distance = stt_gps.get_near_station_gps(self.gps_x, self.gps_y)
        subway_dict = ssub.get_near_subway(self.gps_x, self.gps_y)
        for subway in subway_dict:
            name_list.append(subway['place_name'])
            distance.append(subway['distance'])

        for i, distance in enumerate(distance):
            # 목적지에서 지하철역까지 거리를 성인 평균 보행 속도 67m/s 를 나누어 지하철역까지의 보행시간 계산
            self.time = self.time - int(distance)/67
            station_name = name_list[i].split()[0]

            for j, sub in enumerate(subway_route):
                if station_name in sub:
                    #아래방향으로 지하철역 확인
                    while(True):
                        if j+cnt >= len(subway_route):
                            cnt = 1
                            tmp_time = 0
                            break
                        # 도착 지하철역 까지의 시간이 처음 입력된 시간을 초과하기 전에 break
                        if tmp_time + int(subway_route[j+cnt][2]) > self.time:
                            if subway_route[j][0] == subway_route[j + cnt][0]:
                                # 같은 지하철 노선인지 확인 후 추가
                                result_station.append(subway_route[j+cnt][1] + ' ' + subway_route[j+cnt][0])
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
                        # 도착 지하철역 까지의 시간이 처음 입력된 시간을 초과하기 전에 break
                        if tmp_time + int(subway_route[j-cnt+1][2]) > self.time:
                            if subway_route[j][0] == subway_route[j - cnt][0]:
                                # 같은 지하철 노선인지 확인 후 추가
                                result_station.append(subway_route[j-cnt][1] + ' ' + subway_route[j-cnt][0])
                            cnt = 1
                            tmp_time = 0
                            break
                        else:
                            tmp_time += int(subway_route[j-cnt+1][2])
                            cnt += 1

        for stt in result_station:
            gps_x, gps_y = StationGps().get_station_gps(stt)
            result_gps.append([gps_x, gps_y])

        return  result_gps



if __name__ == '__main__':

    print(subway_route)
    '''
    sub = SubwayDestination(127.0816985, 37.5642135, 20)
    print(sub.result_sub_station())
    
    print('시간1')
    spd = SubwayPathData()
    print(spd.subway_path(127.0816985, 37.5642135, 127.021653112054, 37.5112018042687))

    print('시간2')
    spd = SubwayPathData()
    print(spd.subway_path(127.0816985, 37.5642135, 127.067991278758, 37.6364765391858))
    '''