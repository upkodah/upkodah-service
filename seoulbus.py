import xml
import requests
from configparser import ConfigParser
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import seoulbuserror as sberr
from grid import geogrid
import pandas as pd
import xmltodict

import time


# 서울특별시 경위도 한계
LONG_UPP = 127.269311  # 서울특별시 경도 상한 X
LONG_LOW = 126.734086  # 서울특별시 경도 하한
LATI_UPP = 37.715133  # 서울특별시 위도 상한 Y
LATI_LOW = 37.413294  # 서울특별시 위도 하한

DFT_RADIUS = 150

def read_key(key_name):
    ''' config.ini에서 API Key를 읽어오는 함수 '''
    try:
        config = ConfigParser()
        config.read('config.ini')

        key = config['API KEY'][key_name]
    except KeyError:
        print(f'KeyError: key_name <{key_name}>에 해당하는 키가 없습니다.')
    except:
        print('ConfigReadError:')
        raise Exception
    else:
        return key.strip('\'')

# 키 직접 코드에 쓸 경우를 위해 아래와 같이 놔 둠.
api_key = read_key('kr.go.data.jsj')

def get_station_by_pos(gps_x, gps_y, radius=DFT_RADIUS):
    '''
    좌표 값 주변의 버스 정류소 출력.
    uri: http://ws.bus.go.kr/api/rest/stationinfo/getStationByPos

    Args:
        gps_x (float): longitude             -> tmX
        gps_y (float): latitude              -> tmY
        radius (int): 정류소 탐색 반경 (meter 단위). default = DFT_RADIUS

    Return:
        arsId_list (list): 검색 좌표 주변의 정류소 ID(ars_id)를 str list로 반환

    Example:
        arslist = get_station_by_pos(126.89151, 37.511111, 200)
    
    Raise:
        Request Error: HTTP 에러 등.
        HeaderCodeError: HTTP Response 200 중 API 상에서 일어난 오류.
    '''
    # 초기화
    _uri = 'http://ws.bus.go.kr/api/rest/stationinfo/getStationByPos'
    _header = {'serviceKey': api_key}       # 코드 상단에서 전역으로 선언된 api_key

    _params = dict()
    _params['tmX'] = gps_x
    _params['tmY'] = gps_y
    _params['radius'] = radius
    
    # API request
    resp = requests.get(_uri, params=_params, headers=_header)

    # TODO: add http excetion
    # http error detected
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()

    bsxml = BeautifulSoup(resp.text, 'lxml-xml')  # Parsing XML

    # 헤더 코드 검사. 검사 대상이 없을 경우, 빈 리스트 반환
    if sberr.inspect_hearder_code(bsxml) in sberr.NO_ITEM_CODE:
        return []

    # item list
    item_list = bsxml.findAll('itemList')
    ars_id_list = []
    for item in item_list:
        # 정류소 id만 반환.
        ars_id_list.append(item.find('arsId').get_text())
    return ars_id_list

def get_route_by_station(ars_id):
    '''
    정류소 id(ars_id)를 입력받아 해당 정류소를 지나는 노선(route_list) 반환
    uri: http://ws.bus.go.kr/api/rest/stationinfo/getRouteByStation
    
    Args:
        ars_id (str): 정류소 ID
    
    Return:
        route_list (list(str)) : 정류소를 지나는 노선 ID 반환

    Raise:
        Request Error: HTTP 에러 등.
        HeaderCodeError: HTTP Response 200 중 API 상에서 일어난 오류.
    
    Example:
        routelist = get_route_by_station(ars_id)         # sample ars_id_list = ['19002', '17947', '17412', '17834', '19001', '17001']


    '''
    # 초기화
    _uri = 'http://ws.bus.go.kr/api/rest/stationinfo/getRouteByStation'
    _header = {'serviceKey':api_key}        # 코드 상단에서 전역으로 선언된 api_key
    # set params
    _params = dict()
    _params['arsId'] = ars_id

    # API request
    resp = requests.get(_uri, params=_params, headers=_header)

    # TODO: add http excetion
    # http error detected
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()

    bsxml = BeautifulSoup(resp.text, 'lxml-xml')  # Parsing XML

    # 헤더 코드 검사. 검사 대상이 없을 경우, 빈 리스트 반환
    if sberr.inspect_hearder_code(bsxml) in sberr.NO_ITEM_CODE:
        return []
    
    # item list
    item_list = bsxml.findAll('itemList')
    route_list = []
    for item in item_list:
        # 노선 id만 반환.
        route_list.append(item.find('busRouteId').get_text())
    return route_list

def get_station_by_route(route_id):
    """
    버스 노선 ID(route_id)를 받아 '경유하는 정류소들의 목록(ars_id_list)' 반환
    uri: http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute

    Args:
        route_id (str) : 버스 노선 id

    Return:
        ars_id_list (list(str)): 경유하는 정류소들의 목록

    Raise:
        Request Error: HTTP 에러 등.
        HeaderCodeError: HTTP Response 200 중 API 상에서 일어난 오류.

    Example:
        ars_id_list = get_station_by_route(route)                       # route = '100100550'

    """
    # 초기화
    _uri = 'http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute'
    _header = {'serviceKey':api_key}        # 코드 상단에서 전역으로 선언된 api_key
    # set params
    _params = dict()
    _params['busRouteId'] = route_id

    # API request
    resp = requests.get(_uri, params=_params, headers=_header)

    # TODO: add http excetion
    # http error detected
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()

    bsxml = BeautifulSoup(resp.text, 'lxml-xml')  # Parsing XML

    # 헤더 코드 검사. 검사 대상이 없을 경우, 빈 리스트 반환
    if sberr.inspect_hearder_code(bsxml) in sberr.NO_ITEM_CODE:
        return []

    # item list
    item_list = bsxml.findAll('itemList')
   
    ars_id_list = []
    for item in item_list:
        # 정류소 id만 반환.
        ars_id_list.append(item.find('arsId').get_text())
    return ars_id_list

def get_station_info_by_route(route_id):
    """
    버스 노선 ID(route_id)를 받아 '경유하는 정류소들의 정보'(dataframe) 반환
    uri: http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute

    Args:
        route_id (str) : 버스 노선 id

    Return:
        station_df (Dataframe): 경유하는 정류소들의 목록 및 정보

    Raise:
        Request Error: HTTP 에러 등.
        HeaderCodeError: HTTP Response 200 중 API 상에서 일어난 오류.

    Example:
        station_df = get_station_by_route(route)                       # route = '100100550'

    """
# 초기화
    _uri = 'http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute'
    _header = {'serviceKey':api_key}        # 코드 상단에서 전역으로 선언된 api_key
    # set params
    _params = dict()
    _params['busRouteId'] = route_id

    # API request
    resp = requests.get(_uri, params=_params, headers=_header)

    # TODO: add http excetion
    # http error detected
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()

    bsxml = BeautifulSoup(resp.text, 'lxml-xml')  # Parsing XML

    # 헤더 코드 검사. 검사 대상이 없을 경우, 빈 리스트 반환
    if sberr.inspect_hearder_code(bsxml) in sberr.NO_ITEM_CODE:
        return []

    # all info of item
    item_dict = xmltodict.parse(resp.text)['ServiceResult']['msgBody']['itemList']
    station_df = pd.DataFrame.from_dict(item_dict)

    # 구간 속력과 구간 거리를 int로 형 변환. - 시간 계산에 사용
    station_df = station_df.astype({'sectSpd': float,'fullSectDist':float})
    # 구간 분속, 구간 소요 시간을 추가.
    station_df['sectMinSpd'] = station_df['sectSpd']*1000/60
    station_df['sectTime'] = station_df['fullSectDist']/station_df['sectMinSpd'] 

    return station_df

def get_non_transfer(start_x, start_y, end_x, end_y, route_id):
    '''
    출발지와 목적지 좌표를 사용하여 환승경로를 탐색하는 API 사용. 
    환승 횟수가 0이면서, 입력된 노선을 이용하는 경로 정보를 반환한다.

    - 두 정류소의 좌표와 노선 id를 입력하여 걸린 시간을 얻는다.

    Args:
        start_x, start_y (float): 출발지 좌표
        end_x, end_y (float): 목적지 좌표               -> 두 정류소의 좌표를 각각 입력하고,
         route_id (str): 노선 id                        -> 두 정류소의 노선을 입력.
    Return:
        non_transfer (Dataframe): 비환승 경유 정보를 반환.

    '''
    # 초기화
    _uri = 'http://ws.bus.go.kr/api/rest/pathinfo/getPathInfoByBus'
    _header = {'serviceKey': api_key}

    # set params
    _params = dict()
    _params['startX'] = start_x
    _params['startY'] = start_y
    _params['endX'] = end_x
    _params['endY'] = end_y

    # API request
    resp = requests.get(_uri, params=_params, headers=_header)

    # TODO: add http excetion
    # http error detected
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()

    bsxml = BeautifulSoup(resp.text, 'lxml-xml')  # Parsing XML

    # 헤더 코드 검사. 검사 대상이 없을 경우, 빈 리스트 반환
    if sberr.inspect_hearder_code(bsxml) in sberr.NO_ITEM_CODE:
        return []

    # all info of item
    item_dict = xmltodict.parse(resp.text)['ServiceResult']['msgBody']['itemList']
    #print(pd.DataFrame.from_dict(item_dict))

    # 환승 횟수가 0인 경우 선택.
    non_transfer = list()
    print('검색된 경로의 환승 횟수:', end=' ')
    for item in item_dict:
        print(len(item['pathList']), end=' ')

        # pathList가 여러 개, 즉 item의 원소 개수가 여러 개이면 환승하는 경우임.
        # 그러므로 len이 1인 경우만 선택.     
        if len(item['pathList']) == 1:
            # route_id와 같은 목록을 선택.
            if item['itemList']['pathList']['routeId'] == route_id:
                print(item)
                return pd.DataFrame.from_dict(item)
            non_transfer.append(item)
    print()
    return pd.DataFrame.from_dict(non_transfer)

def get_location_by_station_name(station_name):
    '''
    정류소 키워드 검색 이용하여 정류소 이름(station_name)을 입력하여 좌표 반환.

    Args:
        station_name (str): station name. 정류소 이름
    
    Return:
        gps_x, gps_y (2 float): 정류소 좌표
    '''
    # 초기화
    _uri = 'http://ws.bus.go.kr/api/rest/pathinfo/getLocationInfo'
    _header = {'serviceKey':api_key}

    # set params
    _params = dict()
    _params['stSrch'] = station_name

    # API 요청
    resp = requests.get(_uri, params=_params, headers=_header)
    
    # TODO: add http excetion
    # http error detected
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()

    bsxml = BeautifulSoup(resp.text, 'lxml-xml')  # Parsing XML

    # 헤더 코드 검사. 검사 대상이 없을 경우, 빈 리스트 반환
    if sberr.inspect_hearder_code(bsxml) in sberr.NO_ITEM_CODE:
        return None

    # item list
    item_list = bsxml.findAll('itemList')
    # 키워드에 가장 근접한 정류소 index=0
    gps_x = item_list[0].find('gpsX').text
    gps_y = item_list[0].find('gpsY').text

    return gps_x, gps_y

def find_station_by_time(gps_x, gps_y, time):
    '''

    '''
    bus_route_list = list()     # 주변의 모든 노선(오류 제외)
    destination_list = list()

    # 입력 좌표 주변 정류소 탐색
    station_list = get_station_by_pos(gps_x, gps_y)
    print('Nearby Busstop: ', station_list)  # 근처 정류장 모두 찾기
    # station_list : 주변 정류소 list

    # 주변 정류소에 대하여
    for station in station_list:
        # 정류소를 지나는 route list
        route_list = get_route_by_station(station)

        # route_list 중 오류가 발생하는 route 제거
        for route in route_list:
            if route not in bus_route_list:
                if route[0] == '1':
                    # 오류나는 버스 노선 제거 (오류나는 버스 노선이 2로 시작)
                    # TODO: 무슨 오류인가?
                    bus_route_list.append(route)
    # bus_route_list: station_list를 지나는 노선 리스트

    print('Nearby Route: ', bus_route_list)  # 정류장이 지나는 버스 노선 찾기

    # dataframe 반환 형식 설정을 위한 columns 초기화
    columns = ['arsId', 'beginTm', 'busRouteId', 'busRouteNm', 'direction', 'gpsX', 'gpsY', 'lastTm', 'posX', 'posY', 'routeType', 'sectSpd', 'section', 'seq', 'station', 'stationNm', 
'stationNo', 'transYn', 'fullSectDist', 'trnstnid', 'sectMinSpd', 'sectTime']

    for route in bus_route_list:

        station_df = get_station_info_by_route(route)

        dest_index_list = list()    # 최종 지점 인덱스 리스트

        # 주변 정류소 id
        for station in station_list:    # row <- station info
            
            # if station in arsId:
            if station in station_df['arsId'].to_list():
                # 주변 정류소를 시작 위치로 설정.
                start_index = station_df[station_df['arsId'] == station].index[0]
                #print('start_index:', start_index)

                req_time = 0    # required time
                cnt = 1

                # 도착 정류장 계산
                while True:
                    # 구간 시간을 더함
                    try:
                        sectTime = station_df.iloc[start_index + cnt]['sectTime']
                        req_time += sectTime
                    except IndexError:
                        #print('노선 끝')
                        break

                    # 소요 시간의 합이 입력 시간을 넘으면 루프 종료.
                    if req_time > time-3:
                        #req_time = int(req_time)
                        break
                    else:
                        cnt += 1
                
                # 목표 인덱스
                dest_index = start_index + cnt - 1

                if station_df.loc[start_index,['direction']].item() == station_df.loc[dest_index,['direction']].item():
                    # 버스가 회차한 경우를 제외하기 위해 방향이 같은 정류장 선택
                    dest_index_list.append(dest_index)
                    dest_index_list.append(dest_index-1)
                    #dest_index_list.append(dest_index-2)

                # 반대 방향
                req_time = 0    # required time
                cnt = -1
                while True:
                    # 구간 시간을 더함
                    try:
                        sectTime = station_df.iloc[start_index + cnt]['sectTime']
                        req_time += sectTime
                    except IndexError:
                        #print('노선 끝')
                        break

                    # 소요 시간의 합이 입력 시간을 넘으면 루프 종료.
                    if req_time > time-3 or start_index + cnt<=1:
                        #req_time = int(req_time)
                        break
                    else:
                        cnt -= 1
                
                # 목표 인덱스
                dest_index = start_index + cnt + 1
                
                if station_df.loc[start_index,['direction']].item() == station_df.loc[dest_index,['direction']].item():
                #     # 버스가 회차한 경우를 제외하기 위해 방향이 같은 정류장 선택
                    dest_index_list.append(dest_index)
                    dest_index_list.append(dest_index+1)
                    #dest_index_list.append(dest_index+2)
                
        # index_list의 중복 제거
        dest_index_list = list(set(dest_index_list))
        #print(f'노선 번호 {route}의 index:', dest_index_list)
        
        dest_subset_df = station_df.iloc[dest_index_list]

        destination_list.extend(dest_subset_df.values.tolist())
    destination_df = pd.DataFrame(destination_list, columns=columns)
    destination_df['time'] = time
    #print(destination_df)
    return destination_df

''' TEST CODE '''
if __name__=='__main__':
    print('=== TEST ===')
    # test get_station_by_pos()
    # gps_x = 126.89151
    # gps_y = 37.511111
    # radius = 200
    # print(f'\n (1) x:{gps_x}, y:{gps_y} 의 반경 {radius}m 안의 정류소')
    # ars_list = get_station_by_pos(gps_x, gps_y, radius)
    # print("arsId list: ", ars_list)

    # # test get_route_by_station(ars_id)
    # if ars_list != None and len(ars_list) > 0:
    #     ars_id = ars_list[0]
    # else:
    #     ars_id = '19999'
    # print(f'\n (2) 정류소 {ars_id}의 노선')
    # route_list = get_route_by_station(ars_id)
    # print("route list: ", route_list)

    # # test get_route_by_station(ars_id)
    # if route_list != None and len(route_list) > 0:
    #     route_id = route_list[0]
    # else:
    #     route_id = '100100550'
    # print(f'\n (3) 노선 {route_id}의 버스 정류소')
    # ars_id_list = get_station_by_route(route_id)
    # print("arsId List: ", ars_id_list)

    # # test get_non_transfer()
    #print(get_non_transfer(126.890001872801,37.5757542035555, 127.04249040816, 37.5804217059895, 100100047))

    # # test get_station_info_by_route()
    #station_df = get_station_info_by_route(100100047)
    #print(list(station_df.columns))
    #station_df['sectSpd'] = station_df['sectSpd']*1000/60
    #station_df['sectTime'] = station_df['fullSectDist']/station_df['sectSpd']    
    #print(station_df.loc[0:5,['sectTime', 'fullSectDist', 'sectSpd']])

    # # test find_station_by_time()
    start_time = time.time()

    lon = 127.054732
    lat = 37.583466 
    keyword = '시립대 정문'
    #df_frame = pd.DataFrame(columns=['keyword','busRouteId', 'arsId', 'gpsX', 'gpsY', 'trans_type', 'time', 'grid_id'])
    #df_frame.to_csv('sample_bus.csv', index=False, header=True, encoding='utf-8')

    for i in range(2,4):
        eta = 10*i

        df = find_station_by_time(lon, lat, eta)
        #print(df)
        df['keyword'] = keyword
        df['trans_type'] = 0
        busstop_df = df.loc[:, ['keyword','busRouteNm', 'stationNm', 'gpsX', 'gpsY', 'trans_type', 'time']].copy()


        print("프로그램 시간: ", time.time() - start_time)
        gg = geogrid.GeoGrid()
        busstop_df = busstop_df.astype({'gpsX':float, 'gpsY':float})

        try:
            for index, row in busstop_df.iterrows():
                busstop_df.loc[index, ['grid_id']] = gg.get_grid_id(row['gpsX'], row['gpsY'])

        except KeyError:
            print("결과가 없습니다.")
