import requests, bs4
import pandas as pd
from urllib.parse import urlencode, quote_plus, unquote

# 판다스 데이터 행 표시 100까지 / 열 표시 10까지
pd.set_option('display.max_row', 100)
pd.set_option('display.max_column', 10)

# API 서비스키 값
My_API_Key = unquote('bhQZulxZSz%2FeMsDseMe2DSccTVB%2BQPnxTxDp4SrK7HYRP%2BS0YDiBn93FLz0d%2FMFbyMPUqAvaMqrtW4e9%2FnHYhA%3D%3D')


class GetLocation:


    def station_name(self, stt_name):

        xmlUrl = 'http://ws.bus.go.kr/api/rest/pathinfo/getLocationInfo'

        queryParams = '?' + urlencode({quote_plus('ServiceKey'): My_API_Key,
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

        queryParams = '?' + urlencode({quote_plus('ServiceKey'): My_API_Key,
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

        direction = []
        seq = []
        section = []
        station = []
        arsId = []
        stationNm = []
        gpsX = []
        gpsY = []

        bus_route_info = {}

        xmlUrl = 'http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute'

        My_API_Key = unquote(
            'bhQZulxZSz%2FeMsDseMe2DSccTVB%2BQPnxTxDp4SrK7HYRP%2BS0YDiBn93FLz0d%2FMFbyMPUqAvaMqrtW4e9%2FnHYhA%3D%3D')

        queryParams = '?' + urlencode({quote_plus('ServiceKey'): My_API_Key,
                                       quote_plus('busRouteId'): self.bus_route})

        response = requests.get(xmlUrl + queryParams).text.encode('utf-8')
        xmlobj = bs4.BeautifulSoup(response, 'lxml-xml')
        itemList_tag = xmlobj.findAll('itemList')

        for i in range(0,len(itemList_tag)):

            direction.append(itemList_tag[i].find('direction').text)
            seq.append(itemList_tag[i].find('seq').text)
            section.append(itemList_tag[i].find('section').text)
            station.append(itemList_tag[i].find('station').text)
            arsId.append(itemList_tag[i].find('arsId').text)
            stationNm.append(itemList_tag[i].find('stationNm').text)
            gpsX.append(itemList_tag[i].find('gpsX').text)
            gpsY.append(itemList_tag[i].find('gpsY').text)


            bus_route_info['진행방향'] = direction
            bus_route_info['순번'] = seq
            bus_route_info['구간ID'] = section
            bus_route_info['정류소ID'] = station
            bus_route_info['정류소번호'] = arsId
            bus_route_info['정류장이름'] = stationNm
            bus_route_info['gpsX'] = gpsX
            bus_route_info['gpsY'] = gpsY

            df = pd.DataFrame(bus_route_info)

            df = df[['진행방향', '순번', '구간ID', '정류소ID', '정류소번호', '정류장이름', 'gpsX', 'gpsY']]

        return df


