import requests, bs4
import pandas as pd
import SeoulBusAPI
import numpy as np
from urllib.parse import urlencode, quote_plus, unquote


# API 서비스키 값
my_api_key = unquote('bhQZulxZSz%2FeMsDseMe2DSccTVB%2BQPnxTxDp4SrK7HYRP%2BS0YDiBn93FLz0d%2FMFbyMPUqAvaMqrtW4e9%2FnHYhA%3D%3D')
service_key = "SVpCy0bvZ5pGxpQdz6HmdUFgFl5L6vUbmK9tzQAPslFjjRHSBsKGTvYAkRC84aHoeUct2mtsiD8YfWyEzOQMIQ%3D%3D"


class GetLocation:


    def station_name(self, stt_name):

        xmlUrl = 'http://ws.bus.go.kr/api/rest/pathinfo/getLocationInfo'

        queryParams = '?' + urlencode({quote_plus('ServiceKey'): my_api_key,
                                       quote_plus('stSrch'): stt_name})

        response = requests.get(xmlUrl + queryParams).text.encode('utf-8')
        xmlobj = bs4.BeautifulSoup(response, 'lxml-xml')
        itemList_tag = xmlobj.findAll('itemList')

        gps_x = itemList_tag[0].find('gpsX').text
        gps_y = itemList_tag[0].find('gpsY').text

        return gps_x, gps_y


class PathData:


    def search(self, start_x, start_y, end_x, end_y, routeId):

        xmlUrl = 'http://ws.bus.go.kr/api/rest/pathinfo/getPathInfoByBusNSub'

        queryParams = '?' + urlencode({quote_plus('ServiceKey'): my_api_key,
                                       quote_plus('startX'): start_x,
                                       quote_plus('startY'): start_y,
                                       quote_plus('endX'): end_x,
                                       quote_plus('endY'): end_y})

        response = requests.get(xmlUrl + queryParams).text.encode('utf-8')
        xmlobj = bs4.BeautifulSoup(response, 'lxml-xml')
        itemList_tag = xmlobj.findAll('itemList')

        for i in range(0,len(itemList_tag)):

            # 버스타고 환승 없이 가는 경로의 시간을 찾는 경우이므로 환승 횟수가 1인 경우를 검색
            pathList_tag = itemList_tag[i].find_all('pathList')

            if len(pathList_tag) == 1 :

                if itemList_tag[i].find('routeId').text == str(routeId) :

                    time = itemList_tag[i].find('time').text

                    station = itemList_tag[i].find('tname').text

        return time,station


class GetStationByBusRoute:


    def __init__(self, bus_route):

        self.bus_route = bus_route

    def search(self):

        directions = []
        seqs = []
        sections = []
        stations = []
        arsIds = []
        stationNms = []
        gpsX_list = []
        gpsY_list = []
        sectSpds = []
        fullSectDists = []

        bus_route_info = {}

        xmlUrl = 'http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute'

        My_API_Key = unquote(
            'bhQZulxZSz%2FeMsDseMe2DSccTVB%2BQPnxTxDp4SrK7HYRP%2BS0YDiBn93FLz0d%2FMFbyMPUqAvaMqrtW4e9%2FnHYhA%3D%3D')

        queryParams = '?' + urlencode({quote_plus('ServiceKey'): my_api_key,
                                       quote_plus('busRouteId'): self.bus_route})

        response = requests.get(xmlUrl + queryParams).text.encode('utf-8')
        xmlobj = bs4.BeautifulSoup(response, 'lxml-xml')
        itemList_tag = xmlobj.findAll('itemList')

        for i in range(0,len(itemList_tag)):

            directions.append(itemList_tag[i].find('direction').text)
            seqs.append(itemList_tag[i].find('seq').text)
            sections.append(itemList_tag[i].find('section').text)
            stations.append(itemList_tag[i].find('station').text)
            arsIds.append(itemList_tag[i].find('arsId').text)
            stationNms.append(itemList_tag[i].find('stationNm').text)
            gpsX_list.append(itemList_tag[i].find('gpsX').text)
            gpsY_list.append(itemList_tag[i].find('gpsY').text)
            sectSpds.append(itemList_tag[i].find('sectSpd').text)
            fullSectDists.append(itemList_tag[i].find('fullSectDist').text)


            bus_route_info['진행방향'] = directions
            bus_route_info['순번'] = seqs
            bus_route_info['구간ID'] = sections
            bus_route_info['정류소ID'] = stations
            bus_route_info['정류소번호'] = arsIds
            bus_route_info['정류장이름'] = stationNms
            bus_route_info['gpsX'] = gpsX_list
            bus_route_info['gpsY'] = gpsY_list
            bus_route_info['구간속도'] = sectSpds
            bus_route_info['구간거리'] = fullSectDists

            df = pd.DataFrame(bus_route_info)

            df = df[['진행방향', '순번', '구간ID', '정류소ID', '정류소번호', '정류장이름', 'gpsX', 'gpsY', '구간속도', '구간거리']]

        return df


class DestinationStation:


    def __init__(self, gps_x, gps_y, time):

        self.gps_x = gps_x
        self.gps_y = gps_y
        self.time = time

    def result_station(self):

        bus_route_list = []
        station_gps_list = []

        bst = SeoulBusAPI.BusStation(service_key)
        station_list = bst.findStation(self.gps_x, self.gps_y)
        print(station_list)  # 근처 정류장 모두 찾기

        for station in station_list:
            get_route = SeoulBusAPI.BusRoute(service_key).getRoute(station)
            for i in get_route:
                if i not in bus_route_list:
                    if i[0] == '1':
                        # 오류나는 버스 노선 제거 (오류나는 버스 노선이 2로 시작)
                        bus_route_list.append(i)

        print(bus_route_list)  # 정류장이 지나는 버스 노선 찾기

        for route in bus_route_list:

            # api에서 제공하는 구간거리, 구간속도를 기준으로 도착 정류장 계산

            df = GetStationByBusRoute(route).search()
            station_num_list = list(np.array(df['정류소번호'].tolist()))
            bus_directions = list(np.array(df['진행방향'].tolist()))
            gps_x_list = list(np.array(df['gpsX'].tolist()))
            gps_y_list = list(np.array(df['gpsY'].tolist()))
            sect_spd_list = list(np.array(df['구간속도'].tolist()))
            sect_dist = list(np.array(df['구간거리'].tolist()))
            station_names = list(np.array(df['정류장이름'].tolist()))

            for station in station_list:

                req_time = 0
                cnt = 1

                if station in station_num_list:
                    start_index = station_num_list.index(station)

                    # 도착 정류장 계산
                    while True:
                        # 속도를 km/h에서 m/m으로 수정
                        meter_per_min = int(sect_spd_list[start_index + cnt]) * 1000 / 60
                        req_time += int(sect_dist[start_index + cnt]) / meter_per_min
                        if req_time > self.time:
                            req_time = int(req_time)
                            break
                        else:
                            cnt += 1

                    dest_index = start_index + cnt - 1
                    if len(station_num_list) - 1 < dest_index:
                        break

                    if bus_directions[start_index] == bus_directions[dest_index]:
                        # 버스가 회차한 경우를 제외하기 위해 방향이 같은 정류장 선택
                        stt_name = station_names[dest_index]
                        one_result = [gps_x_list[dest_index],gps_y_list[dest_index], req_time, stt_name]

                        if one_result not in station_gps_list:
                            # 중복되는 결과 제외
                            station_gps_list.append(one_result)
                        '''
                        print(gps_x[start_index], gps_y[start_index], gps_x[dest_index], gps_y[dest_index])
                        print('소요시간 : ', req_time)
                        print('도착 정류장 : ' + stt_name)
                        '''

        return station_gps_list

    def show_result(self):
        station_list = self.result_station()
        for i in station_list:
            print(i)
