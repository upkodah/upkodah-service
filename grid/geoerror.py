# grid/geoerror.py
import grid.geoconst as gcon

class GridIdLengthError(Exception):
    """
    Exception raised for errors in the input.

    Attributes:
        grid_id
        message -- explanation of the error
    """
    def __init__(self, grid_id,
    message = f'입력된 Grid ID의 길이가 유효하지 않습니다. 입력 Grid ID의 길이는 {gcon.GRID_ID_LENGTH}자이어야 합니다.'):
        self.grid_id = grid_id
        self.message = message
        super().__init__(message)
    
    def __str__(self):
        return f'{self.message} | Grid ID: {self.grid_id}'

class LongitudeRangeError(Exception):
    '''   경도 좌표 범위 초과 에러    '''
    def __init__(self, lon,
    message = f'Longitude is not in range ({gcon.KOR_BND_LEFT}, {gcon.KOR_BND_RIGHT})'):
        self.lon = lon
        self.message = message
        super().__init__(message)
    
    def __str__(self):
        return f'{self.message} | longitude: {self.lon}'

class LatitudeRangeError(Exception):
    '''   위도 좌표 범위 초과 에러    '''
    def __init__(self, lat,
    message = f'Latitude is not in ({gcon.KOR_BND_LOW}, {gcon.KOR_BND_UPP}) range'):
        self.lat = lat
        self.message = message
        super().__init__(message)
    
    def __str__(self):
        return f'{self.message} | latitude: {self.lat}'

class GridRangeError(Exception):
    '''    그리드 범위 초과 에러    '''
    def __init__(self, grid_val, lower_bound, upper_bound,
    message = f'Grid Value is not in range'):
        self.grid_val = grid_val
        self.message = message
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        super().__init__(message)
    
    def __str__(self):
        return f'{self.message} ({self.lower_bound}, {self.upper_bound}) | grid_value: {self.grid_val}'

class InvalidGridValueError(Exception):
    def __init__(self, message='Invalid Grid Value'):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message