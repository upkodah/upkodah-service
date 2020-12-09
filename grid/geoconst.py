# grid/geoconst.py

# 서울 중심 좌표
SEOUL_MID_LON = 127.0016985
SEOUL_MID_LAT = 37.5642135

# 서울시립대학교 좌표
UOS_LON = 127.059018
UOS_LAT = 37.583887

def dms2degree(degree, min, sec):
        '''
        도,분,초 형식 좌표(DMS)를 도 형식 좌표(DMM)로 변환하는 함수
        '''
        coord_dec = degree + min/60 + sec/3600
        return coord_dec

# latitude bound
KOR_BND_UPP = dms2degree(43, 0, 36)                         # 43도 00분 36초
KOR_BND_LOW = dms2degree(32, 7, 22)                       # 32도 07분 22초
# longitude bound
KOR_BND_RIGHT = dms2degree(131, 52, 22)                      # 131도 52분 22초
KOR_BND_LEFT = dms2degree(124, 10, 47)                         # 124도 10분 47초

LON_GRID_SIZE = 0.0036
LAT_GRID_SIZE = 0.0036               # 그리드 분할 방식에 따라 달라질 수 있다.

GRID_ID_LENGTH = 8
X_ID_LENGTH = 4
