# grid/geogrid.py
import math
import grid.geoconst as gcon
import grid.geoerror as gerr

class GeoGrid:
    '''
        그리드 시스템을 만들기 위한 클래스

        ** grid_id 획득 전에 객체를 생성하여야 합니다.


    Members: 그리드 시스템 구성에 필요한 멤버 변수로, geoconst의 상수 값들을 디폴트로 합니다.
        bound_up, bound_low, bound_right, bound_left (float): 극단 좌표 ; default (KOR_BND)

        std_lat, std_lon (float): 위도와 경도의 기준 좌표 ; default = 구글 서울시립대 좌표(UOS_LAT, UOS_LON)

        grid_siz_lat, grid_siz_lon (float): 그리드 분할 크기 ;default = 0.0036

    '''
    grid_range_lon = 0
    grid_range_lat = 0

    def __init__(self,
                 bound_right = gcon.KOR_BND_RIGHT, bound_left = gcon.KOR_BND_LEFT,
                 bound_up = gcon.KOR_BND_UPP, bound_low = gcon.KOR_BND_LOW,
                 lon_std = gcon.UOS_LON, lat_std = gcon.UOS_LAT, 
                 lon_grid_size = gcon.LON_GRID_SIZE,  lat_grid_size = gcon.LAT_GRID_SIZE):
        '''
            북.남.동.서.의 극단 좌표, 그리드를 그릴 기준 좌표, 그리드 사이즈를 입력받아 클래스 생성
            위도 경도의 그리드 범위까지 초기화한다.
        '''
        # bound 초기화
        self.bound_right = bound_right
        self.bound_left = bound_left
        self.bound_up = bound_up
        self.bound_low = bound_low
        # 기준 좌표 초기화
        self.std_lon = lon_std
        self.std_lat = lat_std
        # 그리드 사이즈
        self.grid_siz_lon = lon_grid_size
        self.grid_siz_lat = lat_grid_size

        # divide longitude grid & set grid_range_lon
        (self._right, self._left) = self.divider(bound_right, bound_left, lon_std, lon_grid_size)
        self.grid_range_lon = self.positive_grid(self._right, self._left)   # 양수화된 범위값

        # divide latitude grid & set grid_range_lat
        (self._up, self._low) = self.divider(bound_up, bound_low, lat_std, lat_grid_size)
        self.grid_range_lat = self.positive_grid(self._up, self._low)       # 양수화된 범위값
      
    ''' inner methods: 
            divider:
            positive_grid:
    '''
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
    
    ''' 사용 목적 메소드

    '''
    def get_grid_id(self, lon, lat):
        '''  입력한 좌표값에 해당하는 그리드를 출력한다.
        Args:
            lon, lat (float): 경도(x), 위도(y) 좌표(WGS84) - 북위와 동경만 허용.

        Returns:
            grid id (str)

        Example:
            GeoGrid.get_grid_id(lon, lat) # x값, y값

        Raise:
            LongitudeRangeError, LatitudeRangeError. 한국 제한 범위로 사용되는 값을 넘어가면, 에러 메시지를 출력합니다.
        '''
        if (lon < self.bound_left) or (self.bound_right < lon):
            raise gerr.LongitudeRangeError(lon)
        if (lat < self.bound_low) or (self.bound_up < lat):
            raise gerr.LatitudeRangeError(lat)
        lon = lon - self.bound_left
        lat = lat - self.bound_low
        grid_lon = math.floor(lon/self.grid_siz_lon)
        grid_lat = math.floor(lat/self.grid_siz_lat)
              
        return literal_grid(grid_lon, grid_lat)

    def grid_center(self, grid_id):
        '''   grid 값을 넣으면 그리드의 중앙 좌표 값을 반환하는 메소드
            
        Args:
            grid_id (str): 그리드 id
        
        Returns:
            "ctr_lon", "ctr_lat":
        
        Raise:
            GridRangeError: 그리드 범위 값을 초과할 경우 에러
        '''
        # 그리드 좌표 - grid_id segmentation
        grid_lon = xgrid(grid_id)
        grid_lat = ygrid(grid_id)
        
        if (grid_lon < 0) or (self.grid_range_lon < grid_lon):
            raise gerr.GridRangeError(grid_lon, 0, self.grid_range_lon)
        if (grid_lat < 0) or (self.grid_range_lat < grid_lat):
            raise gerr.GridRangeError(grid_lat, 0, self.grid_range_lat)
        
        ctr_lon = self.bound_left + self.grid_siz_lon * (grid_lon + 0.5)
        ctr_lat = self.bound_low + self.grid_siz_lat * (grid_lat + 0.5)

        return [ctr_lon, ctr_lat]

    def coord_center(self, lon, lat):
        ''' 좌표 값에서 그리드 중앙 좌표를 찾는 메소드
        '''
        grid_id = self.get_grid_id(lon, lat)
        return self.grid_center(grid_id)

def read_location(location):
    '''
        리스트 읽기, 문자열 읽기.
    '''
    if location is list and len(location) == 2:
        return [location[0], location[1]]
    elif location is str:
        location.lstrip('[')
        location.rstrip(']')
        loclist = location.split(',')
        return [loclist[0], loclist[1]]
    else:
        return None # raise error

''' xgrid, ygrid: grid_id의 x_grid값과 y_grid 값을 추출하는 메소드 '''
def is_grid_id(grid_id):
    if type(grid_id) is not str:                    # string type 검사
        raise TypeError
    elif len(grid_id) != gcon.GRID_ID_LENGTH:   # grid_id 길이 검사
        raise gerr.GridIdLengthError
    else:
        return True

def xgrid(grid_id):
    if is_grid_id(grid_id):
        return int(grid_id[0:gcon.X_ID_LENGTH])
    else:
        raise gerr.InvalidGridValueError

def ygrid(grid_id):
    if is_grid_id(grid_id):
        return int(grid_id[gcon.X_ID_LENGTH:])
    else:
        raise gerr.InvalidGridValueError

def literal_grid(glon, glat):
    ''' x, y 구분되어있는 grid segment를 하나의 grid_id로 만드는 메소드
    '''
    # 그리드 길이 list 생성
    g_literal = [0 for i in range(gcon.GRID_ID_LENGTH)]
    # 0 ~ x_id 범위까지 
    for i in range(0,gcon.X_ID_LENGTH):
        g_literal[gcon.X_ID_LENGTH-i-1] = str(glon%10)
        glon = int(glon/10)
    # x_id 범위부터 grid_id 범위까지
    for i in range(gcon.X_ID_LENGTH, gcon.GRID_ID_LENGTH):
        g_literal[gcon.GRID_ID_LENGTH + gcon.X_ID_LENGTH - i -1] = str(glat%10)
        glat = int(glat/10)
    g_literal = "".join(g_literal)
    return g_literal

# test get_grid_id
if __name__ == "__main__":
    cgrid = GeoGrid()
    grid_id = cgrid.get_grid_id(127.100637, 37.072855)
    print(f"grid ID: {grid_id}")
