import requests
from bs4 import BeautifulSoup
import pandas as pd
import seoulbus as sb
import seoulsubway as ssub

subway_route = pd.read_csv('subway_with_time.csv', encoding='utf-8')
subway_route.astype({'time':float})

def get_path_by_subway(start_x, start_y, end_x, end_y):

    url = 'http://ws.bus.go.kr/api/rest/pathinfo/getPathInfoBySubway'

    header = {'serviceKey':sb.read_key('kr.go.data.jsh')}

    params = dict()
    params['startX'] = start_x
    params['startY'] = start_y
    params['endX'] = end_x
    params['endY'] = end_y

    resp = requests.get(url, params=params, headers=header)
    xmlobj = BeautifulSoup(resp.text, 'lxml-xml')
    item_list = xmlobj.findAll('itemList')

    time = None
    for item in item_list:

        # 지하철 타고 환승 없이 가는 경로의 시간을 찾는 경우이므로 환승 횟수가 1인 경우를 검색
        path_list= item.find_all('pathList')

        if len(path_list) == 1 :
            time = item.find('time').text            

    return time

def get_station_gps(st_name):
    ''' 지하철 역의 좌표를 얻는 함수   '''
    subway_df = pd.read_csv('subway_naver_more.csv')
    st = subway_df[subway_df['displayName'] == st_name]
    if len(st) == 0:
        return get_station_gps_rq(st_name)
    return st['x'].values[0], st['y'].values[0]

def get_station_gps_rq(st_name):
    ''' 지하철 역 좌표 획득 리퀘스트

    Args:
        stt_name:
    Return:
        gps_x, gps_y
    '''
    _url = 'http://ws.bus.go.kr/api/rest/pathinfo/getLocationInfo'
    _header = {'ServiceKey': sb.read_key('kr.go.data.jsh')}

    # set params
    _params = dict()
    _params['stSrch'] = st_name.replace('역','')

    # API 요청
    resp = requests.get(_url, params=_params, headers=_header)
    xmlobj = BeautifulSoup(resp.text, 'lxml-xml')

    item_list = xmlobj.findAll('itemList')
    if len(item_list) == 0:
        return None, None
    gps_x = item_list[0].find('gpsX').text
    gps_y = item_list[0].find('gpsY').text

    return gps_x, gps_y


def find_station_by_eta(gps_x, gps_y, eta):

    result_df = pd.DataFrame(columns=['idx', 'lane', 'name', 'time', 'cumulative'])

    cnt = 1
    #tmp_time = 0

    near_df = pd.DataFrame(ssub.get_near_subway(gps_x, gps_y))
    print('주변 지하철: ', str(near_df['place_name'].values).strip('[]\''))

    for index, row in near_df.iterrows():
        # 목적지에서 지하철역까지 거리를 성인 평균 보행 속도 80m/s(67) 를 나누어 지하철역까지의 보행시간 계산
        walk_time = int(row['distance'])/80
        sub_time = eta - walk_time
        print('요청 지하철 시간: ', sub_time)

        station_name, lane = row['place_name'].split()

        departure = subway_route[subway_route['name'] == station_name]
        #print(departure)
        idx_depart = departure['idx'].values[0]
        #print(idx_depart)

        up_df = subway_route[(subway_route['lane'] == lane) & (subway_route['idx'] > idx_depart)].copy()
        down_df = subway_route[(subway_route['lane'] == lane) & (subway_route['idx'] < idx_depart)].copy()

        # 각 라인의 상행선 하행선의 누적시간을 계산.
        up_sum = up_df['time'].sum()
        down_sum = down_df['time'].sum()
        #print(up_sum)
        #print(down_sum)

        # 각 호선에 대하여 누적 시간 계산
        tmp_time = 0
        for i, sub in up_df.iterrows():
            tmp_time += sub['time']
            up_df.loc[i, ['cumulative']] = tmp_time

        tmp_time = down_sum
        for i, sub in down_df.iterrows():
            down_df.loc[i, ['cumulative']] = tmp_time
            tmp_time -= sub['time']

        #print(up_df)
        #print(down_df)

        up_result = up_df[(sub_time - 10 < up_df['cumulative']) & (up_df['cumulative'] <= sub_time)].copy()
        down_result = down_df[(sub_time - 10 < down_df['cumulative']) & (down_df['cumulative'] <= sub_time)].copy()
        up_result['cumulative'] += walk_time
        down_result['cumulative'] += walk_time

        #print('시간 내 결과')
        #print(up_result)
        #print(down_result)
        
        #if not up_result.empty:
        result_df = result_df.append(up_result, ignore_index=True)
        #if not down_result.empty:
        result_df = result_df.append(down_result, ignore_index=True)

    #print(result_df)
    for index, station in result_df.iterrows():
        gps_x, gps_y = get_station_gps(station['name'])
        result_df.loc[index, ['x']] = gps_x
        result_df.loc[index, ['y']] = gps_y
        #result_gps.append([gps_x, gps_y])

    return  result_df

if __name__ == '__main__':
    # 시간 - 지하철 정보
    #print(subway_route)
    print(get_station_gps('뚝섬유원지역'))
    
    # test
    print(find_station_by_eta(127.0816985, 37.5642135, 20))
    
    # print('시간1')
    # print(get_path_by_subway(127.0816985, 37.5642135, 127.021653112054, 37.5112018042687))

    # print('시간2')
    # print(get_path_by_subway(127.0816985, 37.5642135, 127.067991278758, 37.6364765391858))
    