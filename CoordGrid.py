import math

# 서울 중심 좌표
SEOUL_MID_LAT = 37.5642135
SEOUL_MID_LON = 127.0016985

def dms2degree(degree, min, sec):
        '''
        도,분,초 형식 좌표(DMS)를 도 형식 좌표(DMM)로 변환하는 함수
        '''
        coord_dec = degree + min/60 + sec/3600
        return coord_dec

# longitude bound
KOR_BND_UPP = dms2degree(43, 0, 36)                         # 43도 00분 36초
KOR_BND_LOW = dms2degree(32, 7, 22)                       # 32도 07분 22초
# latitude bound
KOR_BND_RIGHT = dms2degree(131, 52, 22)                      # 131도 52분 22초
KOR_BND_LEFT = dms2degree(124, 10, 47)                         # 124도 10분 47초

GRID_SIZ = 0.0036               # 그리드 분할 방식에 따라 달라질 수 있다.


class CoordGrid:
    '''
    Members:
        bound_up, bound_low, bound_right, bound_left (float): 극단 좌표 ; default (KOR_BND)
        std_lat, std_lon (float): 위도와 경도의 기준 좌표 ; default = 위키 서울 좌표(SEOUL_MID_LAT, SEOUL_MID_LON)
        grid_siz_lat, grid_siz_lon (float): 그리드 분할 크기 ;default = 0.0036

    '''
    grid_range_lat = 0
    grid_range_lon = 0

    def __init__(self, bound_up = KOR_BND_UPP, bound_low = KOR_BND_LOW,
                 bound_right = KOR_BND_RIGHT, bound_left = KOR_BND_LEFT, 
                 lat_std = SEOUL_MID_LAT, lon_std = SEOUL_MID_LON,
                 lat_grid_siz = GRID_SIZ, lon_grid_siz = GRID_SIZ):
        '''
            북.남.동.서.의 극단 좌표, 그리드를 그릴 기준 좌표, 그리드 사이즈를 입력받아 클래스 생성
            위도 경도의 그리드 범위까지 초기화한다.
        '''
        # 초기화
        self.bound_up = bound_up
        self.bound_low = bound_low
        self.bound_right = bound_right
        self.bound_left = bound_left
        self.std_lat = lat_std
        self.std_lon = lon_std
        self.grid_siz_lat = lat_grid_siz
        self.grid_siz_lon = lon_grid_siz

        # divide latitude grid & set grid_range_lat
        (self._up, self._low) = self.divider(bound_up, bound_low, lat_std, lat_grid_siz)
        self.grid_range_lat = self.positive_grid(self._up, self._low)       # 양수화된 범위값
        # divide longitude grid & set grid_range_lon
        (self._right, self._left) = self.divider(bound_right, bound_left, lon_std, lon_grid_siz)
        self.grid_range_lon = self.positive_grid(self._right, self._left)   # 양수화된 범위값

    def divider(self, end_high, end_low, std, grid_siz):
        ''' 초기화시 사용되는 내부용 메소드.
            그리드를 분할하는 메소드. 경도 위도 각각에 수행.
            
        Args:
             end_high, end_low (float): 경도 또는 위도의 극값. (대한민국의 최극단)
             std (float): standard. grid를 분할할 기준점이 된다. 기준 부근의 거리-좌표 정확도가 높음.
             grid_siz (float): grid를 분할할 크기.

        Returns:
            float tuple(2): 

        '''
        n_end_high = math.ceil((end_high - std)*10000)
        n_end_low = math.floor((end_low - std)*10000)
        n_grid = math.floor(grid_siz*10000)

        share_high = n_end_high/n_grid     # 윗 몫
        share_low = n_end_low/n_grid       # 아랫 몫

        print("-- share_high: ", share_high, "share_low: ", share_low)      # print share for debug

        return (share_high, share_low)

    def positive_grid(self, share_high, share_low):
        ''' 내부용 메소드.
            아랫 몫만큼 밀어내어 grid_id값들을 양수화한다.
            0 ~ (share_high-share_low) 범위의 몫 값을 얻어낸다.
            음수(정규화된 그리드)를 사용할 경우 제거한다.
        
        Args:
            share_high, share_low: grid_siz로 나누어진 극점의 값들.

        Return:
            float(or ceiled integer): 그리드의 상한 범위 값.
        '''
        share_high = share_high - share_low
        share_low = 0
        # share_low = 0 이므로 높은 값만 반환. (ceiling)
        share_high = math.ceil(share_high)
        return share_high

    def get_grid_id(self, lat, lon):
        '''  입력한 좌표값에 해당하는 그리드를 출력한다.
        Args:
            lat, lon(float): 위도, 경도 좌표(WGS84) - 북위와 동경만 허용.

        Returns:
            dictionary(2 int): "grid_lat", "grid_lon" 위도와 경도의 grid id
        '''
        if self.bound_left > lon or self.bound_right < lon:
            print("범위 초과")
        if self.bound_low > lat or self.bound_up < lat:
            print("범위 초과")
        lon = lon - self.bound_left
        lat = lat - self.bound_low
        grid_lon = math.floor(lon/self.grid_siz_lon)
        grid_lat = math.floor(lat/self.grid_siz_lat)
        
        # 튜플로 처리할까 고민, 딕셔너리의 출력이 깔끔해서 놔둠.
        return {'grid_lat': grid_lat, 'grid_lon': grid_lon}

    def grid_center(self, grid_lat, grid_lon):
        '''   grid 값을 넣으면 그리드의 중앙 좌표 값을 반환하는 메소드
            
        Args:
            grid_lat, grid_lon: 위,경도 그리드 값
        
        Returns:
            "ctr_lat", "ctr_lon":

        '''
        if grid_lat < 0 or grid_lat > self.grid_range_lat:
            print("범위 초과")
        if grid_lon < 0 or grid_lon > self.grid_range_lon:
            print("범위 초과")

        ctr_lat = self.bound_low + self.grid_siz_lat * (grid_lat + 0.5)
        ctr_lon = self.bound_left + self.grid_siz_lon * (grid_lon + 0.5)

        return {'ctr_lat': ctr_lat, 'ctr_lon': ctr_lon}



    def coord_center(self, lat, lon):
        grid_id = self.get_grid_id
        return self.grid_center(grid_id['grid_lat'], grid_id['grid_lon'])


if __name__ == "__main__":
    print("대한민국 최서단: " + str(KOR_BND_LEFT))
    print("대한민국 최동단: " + str(KOR_BND_RIGHT))
    print("대한민국 최북단: " + str(KOR_BND_UPP))
    print("대한민국 최남단: " + str(KOR_BND_LOW))

    cgrid = CoordGrid()
    #print(cgrid.get_grid_id(37.544444, 127.22222222))

    grid_lat = 1515
    grid_lon = 800
    print("\n\n({}, {} 그리드의 중앙 좌표:".format(grid_lat, grid_lon), end=' ')
    ctr_coord = cgrid.grid_center(1515, 800)
    print(ctr_coord)

    print("확인 ", end='')
    print(cgrid.get_grid_id(ctr_coord['ctr_lat'], ctr_coord['ctr_lon']))


