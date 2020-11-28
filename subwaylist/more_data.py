import get_naver_code as nc
import pandas as pd

def get_subway_dict(code):
    ''' 유효한 코드에서 실행시킬 코드
    '''
    subway_info = dict()
        
    json = nc.get_extern_by_naver_code(code)

    # 찾기 실패
    if 'status' in json:
        pass
    # 찾기 성공
    else:
        sub_json = json[0]
        # dict 생성
        subway_info['id'] = sub_json['id']
        subway_info['name'] = sub_json['name']
        subway_info['longName'] = sub_json['longName']
        subway_info['displayName'] = sub_json['displayName']
        subway_info['displayCode'] = sub_json['displayCode']
        subway_info['x'] = sub_json['point']['x']
        subway_info['y'] = sub_json['point']['y']
        subway_info['LaneType'] = sub_json['subwayLaneType']['id']
        subway_info['LaneName'] = sub_json['subwayLaneType']['name']
        subway_info['LaneShort'] = sub_json['subwayLaneType']['shortName']

        #print(json)   

    return subway_info


if __name__ =='__main__':
    naver_code_df = pd.read_csv('subwaylist\\subway_naver.csv', encoding='CP949')
    code_list = naver_code_df['id'].to_list()

    new_list = list()

    for code in code_list:
        new_list.append(get_subway_dict(code))
        print(f'code no {code} appended.')
    print('\nReading Operation ended.')

    new_df = pd.DataFrame(new_list)
    # commit data
    new_df.to_csv('subway_naver_more.csv', mode='a', index=False)
    print('\nMake CSV completed.')