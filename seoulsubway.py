import requests
import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup
from requests.models import HTTPError
import seoulbus as sb
from haversine import haversine
import seoulbuserror as sberr

from grid import geogrid

import time

DFT_RADIUS = 500
WALKING_SPD = 80    # meter per minute
TOLERANCE = 5

def get_near_subway(x, y, radius=DFT_RADIUS):
    '''
    카카오 로컬 api중 카테고리 검색을 이용하여, 근처 지하철역 검색.

    Args:
        x, y (float): 지리 좌표
        radius (int): 반경(m)
    
    Return:
        subway_dict: 주변 지하철 역의 데이터를 포함하는 dict
            
    '''

    _uri = 'https://dapi.kakao.com/v2/local/search/category.json'
    _header = {'Authorization': 'KakaoAK ' + sb.read_key('kakaolocal.jsj')}
    
    _params = dict()
    _params['category_group_code'] = 'SW8'      # 지하철 카테고리 검색
    _params['x'] = x
    _params['y'] = y
    _params['radius'] = radius

    resp = requests.get(_uri, params=_params, headers=_header)

    if resp.status_code != requests.codes.ok:
        print(f'HTTP ERROR: RESPONSE <{resp.status_code}>')
        raise HTTPError

    # API 결과가 없을 경우
    meta_dict = resp.json()['meta']
    if meta_dict['total_count'] == 0:
        return []

    # 호선 정보 추가.
    subway_list = resp.json()['documents']
    #print(subway_list)
    for subway in subway_list:
        lane = subway['place_name'].split(' ')[-1]
        subway['lane'] = lane

    # actually list of dict
    return subway_list

def get_walking_time_to_subway(near_subway_list):
    '''
    근처 역까지 소요시간 재기. 상수 WALKING_SPD 참조.
    
    Args:   subway_dict: get_near_subway의 반환 값.
    '''
    time_list = list()
    for subway in near_subway_list:
        #print('distance: ', subway['distance'])
        time_list.append(int(subway['distance'])/WALKING_SPD)
    return time_list

def get_time_by_subway(start_x, start_y, end_x, end_y):
    '''
    지하철 위치를 입력하고 시간을 반환하는 함수

    주의! 현재 500 HTTP 에러 다발.
    
    Args: 
          start_x, start_y, end_x, end_y (float): 출발지, 목적지 지하철 역의 경위도.
    Return:
            time | None

    Raise:
            HTTP error
    '''

    _url_base = 'http://ws.bus.go.kr/api/rest/pathinfo/getPathInfoBySubway'

    _header = {'serviceKey':sb.read_key('kr.go.data.jsh')}

    _params = dict()
    _params['startX'] = start_x
    _params['startY'] = start_y
    _params['endX'] = end_x
    _params['endY'] = end_y
    
    resp = requests.get(_url_base, params=_params, headers=_header)
    # http error
    if resp.status_code != requests.codes.ok:
        #print(f'HTTP ERROR: RESPONSE <{resp.status_code}>')
        resp.raise_for_status()

    bsxml = BeautifulSoup(resp.text, 'lxml-xml')
    # 헤더 코드 검사. 검사 대상이 없을 경우, 빈 리스트 반환
    if sberr.inspect_hearder_code(bsxml) in sberr.NO_ITEM_CODE:
        return 0

    item_list = bsxml.findAll('itemList')
    
    time_list = list()
    for item in item_list:
        time_list.append(float(item.find('time').text))
    #print(time_list)
    if len(time_list) == 0:
        return 0
    else:
        return time_list[0]

def get_time_by_subway_n(start_scode, goal_scode):
    '''
    현재 시간대의 도착 예상 시간을 반환. 

    '''
    if str(start_scode) == str(goal_scode):
        return 0

    _url_base = 'https://map.naver.com/v5/api/subway/search'
    _params = dict()
    _params['start'] = start_scode
    _params['goal'] = goal_scode
    now = datetime.now()
    _params['departureTime'] = now.strftime('%Y-%m-%d') + 'T' + now.strftime('%H:%M:%S')
    # 예시: 2020-11-28T20%3A04%3A55

    resp = requests.get(_url_base, params=_params)
    # http error
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()
    arrival_dict = resp.json()

    if arrival_dict['context'] == None:
        return 0
    elif 'path' in arrival_dict and len(arrival_dict['path']) == 0:
        return 0
    else:
        duration = arrival_dict['paths'][0]['duration']
        #print('duration: ', duration)
        return duration

def get_intime_subway(gps_x, gps_y, eta):
    '''
    시간 안에 도달하는 지하철을 반환

    Args:
        gps_x (float)
        gps_y (float)
        eta (numeric) float / int : estimated time of arrival 
    '''

    # 근처 지하철 탐색.
    near_subway_list = get_near_subway(gps_x, gps_y)

    if len(near_subway_list) == 0:
        print('주변 지하철 역이 존재하지 않습니다')
        return None

    near_subway_df = pd.DataFrame(near_subway_list)
    # 도보 시간 리스트
    walk_time_list = get_walking_time_to_subway(near_subway_list)
    print(f'입력 좌표 값 x: {gps_x}, y: {gps_y}')

    lanes = list(set(near_subway_df['lane'].tolist()))
    print('근처 지하철 역:', near_subway_df['place_name'].tolist())
    print('근처 호선: ', lanes)
    
    # load data
    all_subway_df = pd.read_csv('subway_naver_more.csv')

    # 불필요한 열 지우기
    all_subway_df.drop(['name', 'LaneType', 'LaneShort'], axis='columns', inplace=True)
    
    destination_df = pd.DataFrame(columns=['id', 'displayName', 'longName', 'displayCode', 'x', 'y', 'LaneName', 'distance', 'time'])

    # 주변 역이 지나는 같은 호선에 대한 요청
    for index, near_subway in near_subway_df.iterrows():
        lane_condition = (all_subway_df['LaneName'] == near_subway['lane'])
        
        subway_x = float(near_subway['x'])
        subway_y = float(near_subway['y'])

        walk_time = walk_time_list[index]
        time_on_subway = eta - walk_time

        # samelane_df : 동일 호선 위의 역들
        samelane_df = all_subway_df[lane_condition].copy()

        # 근처 역과 다른 역 사이의 거리를 잰다 - API 사용량 줄이기
        for index, station in samelane_df.iterrows():
            s_x = station['x']
            s_y = station['y']
            h = haversine((subway_x, subway_y),(s_x, s_y))
            #print(f'{subway_x},{subway_x} 와 {s_x},{s_y}의 거리:{h}')
            samelane_df.loc[index, ['distance']] = h
        # 2km 정도에 10분 내외의 도착시간을 가지므로, 오차 범위를 두어 API 범위를 줄임.
        distance_condition = ((time_on_subway/5 - 0) < samelane_df['distance']) &(samelane_df['distance'] < (time_on_subway/5 + 5))
        around_df = samelane_df[distance_condition].copy()
        #print(around_df)

        # 지하철 사이 시간 열 추가.(API 사용)
        time_list = list()
        for index, station in around_df.iterrows():
            ''' A) 서울교통공사 API 사용 메소드: 현재 500 HTTP 에러 발생 중 '''
            #time_list.append(get_time_by_subway(subway_x,subway_y, station['x'], station['y']))
            ''' B) 네이버 API 사용 메소드: '''
            start_scode = samelane_df[samelane_df['longName'] == near_subway['place_name']]['id']
            goal_scode = station['id']
            time_list.append(get_time_by_subway_n(start_scode, goal_scode))

        around_df.insert(0, 'time', time_list)
        # 시간 조건. 
        # 지하철 위의 시간(time_on_subway)이 시간 결과(around_df['time'])에 맞음. 오차 TOLERANCE에서 하향 조정.
        condition = ((time_on_subway - TOLERANCE-5) < around_df['time']) & (around_df['time'] < (time_on_subway + TOLERANCE-3))

        tmp_df = around_df[condition].copy()

        tmp_df['time'] = tmp_df['time'] + walk_time
        destination_df = pd.concat([destination_df,tmp_df], axis=0, ignore_index=True)

    destination_df.reset_index()
    return destination_df

if __name__ == '__main__':
    # test get_near_subway
    lon = 127.1515
    lat = 37.5975
        
    gg = geogrid.GeoGrid()
    
    for i in range(4, 5):
        eta = 10*i

        start_time = time.time()
        df = get_intime_subway(lon, lat, eta)
        df['lon'] = lon
        df['lat'] = lat
        #df['keyword'] = keyword
        df['transType'] = 1
        #print('결과')
        #print(df)
        print('소요 시간: ', time.time() - start_time)

        if len(df) == 0:
            continue
        for index, row in df.iterrows():
            df.loc[index, ['gridId']] = gg.get_grid_id(row['x'], row['y'])

        sub_df = df.loc[:,['lon','lat', 'keyword', 'displayName', 'LaneName', 'transType', 'time','x', 'y', 'gridId']].copy()

