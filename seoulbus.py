import xml
import requests
from configparser import ConfigParser
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import seoulbuserror as sberr
#import xmltodict

# 서울특별시 경위도 한계
LONG_UPP = 127.269311  # 서울특별시 경도 상한 X
LONG_LOW = 126.734086  # 서울특별시 경도 하한
LATI_UPP = 37.715133  # 서울특별시 위도 상한 Y
LATI_LOW = 37.413294  # 서울특별시 위도 하한

DFT_RADIUS = 150


def read_key():
    ''' config.ini에서 API Key를 읽어오는 함수 '''
    try:
        config = ConfigParser()
        config.read('config.ini')

        key_dict = config['API KEY']
    except:
        print('ConfigReadError:')
        raise Exception
    else:
        return key_dict['kr.go.data.jsj'].strip('\'')

# 키 직접 코드에 쓸 경우를 위해 아래와 같이 놔 둠.
api_key = read_key()

def get_station_by_pos(gpsX, gpsY, radius=DFT_RADIUS):
    '''
    좌표 값 주변의 버스 정류소 출력.
    uri: http://ws.bus.go.kr/api/rest/stationinfo/getStationByPos

    Args:
        gpsX (float): longitude             -> tmX
        gpsY (float): latitude              -> tmY
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
    _params['tmX'] = gpsX
    _params['tmY'] = gpsY
    _params['radius'] = radius
    
    # API request
    resp = requests.get(_uri, params=_params, headers=_header)

    # TODO: add http excetion
    # http error detected
    if resp.status_code != requests.codes.ok:
        print(f'HTTP ERROR: RESPONSE <{resp.status_code}>')
        return None


    
    bsxml = BeautifulSoup(resp.text, 'lxml-xml')  # Parsing XML

    # 헤더 코드 검사. 검사 대상이 없을 경우, 빈 리스트 반환
    if sberr.inspect_hearder_code(bsxml) in sberr.NO_ITEM_CODE:
        return []
    
    # item_list as OrderedList
    # item_list = xmltodict.parse(resp.text)['ServiceResult']['msgBody']['itemList']
    # for item in item_list:
    
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
        print(f'HTTP ERROR: RESPONSE <{resp.status_code}>')
        return None

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

def get_station_by_route(route):
    """
    버스 노선 ID(route)를 받아 '경유하는 정류소들의 목록(ars_id_list)' 반환
    uri: http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute

    Args:
        route (str) : 버스 노선 id

    Return:
        ars_id_list (list(str)): 경유하는 정류소들의 목록

    Raise:
        Request Error: HTTP 에러 등.
        HeaderCodeError: HTTP Response 200 중 API 상에서 일어난 오류.

    Example:


    """
    # 초기화
    _uri = 'http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute'
    _header = {'serviceKey':api_key}        # 코드 상단에서 전역으로 선언된 api_key
    # set params
    _params = dict()
    _params['busRouteId'] = route

    # API request
    resp = requests.get(_uri, params=_params, headers=_header)

    # TODO: add http excetion
    # http error detected
    if resp.status_code != requests.codes.ok:
        print(f'HTTP ERROR: RESPONSE <{resp.status_code}>')
        return None

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


if __name__=='__main__':
    print('=== TEST ===')
    # test get_station_by_pos()
    gpsX = 126.89151
    gpsY = 37.511111
    radius = 200
    print(f'\n(1) x:{gpsX}, y:{gpsY} 의 반경 {radius}m 안의 정류소')
    ars_list = get_station_by_pos(gpsX, gpsY, radius)
    print("arsId list: ", ars_list)

    # test get_route_by_station(ars_id)
    print(f'\n(2) 정류소 {ars_list[0]}의 노선')
    route_list = get_route_by_station(ars_list[0])
    print("route list: ", route_list)

    print(f'\n(3) 노선 {route_list[0]}의 버스 정류소')
    ars_id_list = get_station_by_route(route_list[0])
    print("arsId List: ", ars_id_list)
