'''
    naver에서 지하철 코드 긇어오기.

'''
import requests
import pandas as pd

def get_extern_by_naver_code(naver_code):

    _uri = 'https://map.naver.com/v5/api/realtime/arrivals'
    _params = dict()
    _params['lang'] = 'ko'
    _params['station[]'] = naver_code
    #?lang=ko&station%5B%5D=1409

    resp = requests.get(url=_uri, params=_params)
    return resp.json()

# 데이터 프레임 만들기
def get_subway_df(alpha, omega):
    valid_code = list()
    subway_list = list()

    for code in range(alpha, omega):
        subway_info = dict()
        
        json = get_extern_by_naver_code(code)

        # 찾기 실패
        if 'status' in json:
            pass
        # 찾기 성공
        else:
            # 유효한 코드 번호 - 로그로 출력
            valid_code.append(code)
            
            sub_json = json[0]
            # dict 생성
            subway_info['id'] = sub_json['id']
            subway_info['name'] = sub_json['name']
            subway_info['longName'] = sub_json['longName']
            subway_info['displayName'] = sub_json['displayName']
            subway_info['displayCode'] = sub_json['displayCode']
            subway_info['x'] = sub_json['point']['x']
            subway_info['y'] = sub_json['point']['y']

            #print(json)
            subway_list.append(subway_info)
    # make dataframe    
    subway_df = pd.DataFrame.from_dict(subway_list)
    print('--valid code: ', valid_code)
    #print(subway_df)
    return subway_df



if __name__ == '__main__':

    # 100개 단위로 읽어오기. 도중에 호스트 연결이 끊길 수 있음.
    for i in range(40, 41):
        _a = i*100
        _z = (i+1)*100
        print(f'Searching valid codes from {_a} to {_z}...')
        subway_df = get_subway_df(_a, _z)
        # commit dataframe to csv
        subway_df.to_csv('subway_naver.csv', mode='a', index=False, header=False)
        print('csv appended...\n')
    # TODO: 100 부터 20000까지 돌리면 오래 걸리고, 연결도 막힌다. 해결책?