from urllib.request import urlopen
from urllib.parse import unquote
from bs4 import BeautifulSoup

# URL
API_STATION = "http://ws.bus.go.kr/api/rest/stationinfo/"
API_ROUTE = "http://ws.bus.go.kr/api/rest/busRouteInfo/"

# 서울특별시 경위도 한계
LONG_UPP = 127.269311       # 서울특별시 경도 상한 X
LONG_LOW = 126.734086       # 서울특별시 경도 하한
LATI_UPP = 37.715133        # 서울특별시 위도 상한 Y
LATI_LOW = 37.413294        # 서울특별시 위도 하한


# header code enum for checking
#headerCd = ("OK", )

class BusStation:           
    '''
    좌표 값을 입력받아 정류소 ID를 저장하는 클래스
    
    클래스 생성 후 findStation 메소드를 실행하여 결과를 얻는다.

    
    [Members]

    gpsX, gpsY
    radius

    numStop
    itemList
    arsIdList
    arsIdStr

    [Methods]
    findStation
    
    (CallBackURL: http://ws.bus.go.kr/api/rest/stationinfo/getStationByPos)
    '''

    def __init__(self, serviceKey):
        '''
        공공 데이터 포털에서 발급받은 Service Key를 입력받아 초기화

        gpsX, gpsY의 default 값은 서울의 중앙 좌표로 정의(을지로 주변)
        '''
        #초기화
        self.serviceKey = unquote(serviceKey)
        self.gpsX = 127.0016985                # 동경 - 경도
        self.gpsY = 37.5642135                # 북위 - 위도
        self.radius = 150
        self.numStop = 0                       # 정류소 개수
        
        # 요청
        requestGPS2Stop = API_STATION + "?serviceKey=" + self.serviceKey + "&tmX" + str(self.gpsX) + "&tmY" + str(self.gpsY) + "&radius" + str(self.radius)
        xmlStation = urlopen(requestGPS2Stop)
        bsStation = BeautifulSoup(xmlStation.read(), 'lxml-xml')
        
        # URL 응답이 있는지 검사
        headerCode = int(bsStation.findAll("headerCd").contents[0])

        ## URL 체크
        if headerCode == 0:
            print(">>> 정상 작동")
        elif headerCode == 3:
            print(">>> 결과 없음")
        else:
            print(">>> API 요청 오류")
        ## URL 체크


    def findStation(self, gpsX, gpsY, radius=150):
        '''
        객체 생성 후 API 요청을 위해 실행하는 메소드. 해당 위치 주변의 정류소를 저장한다.
        정류소가 0개일 경우 검색 반경을 넓혀서 재요청한다.
        정류소 목록을 반환한다.
        
        [params]
        (param1) serviceKey:  서비스 키
        (param2) gpsX:        경도(126~127.xxxxxx)
        (param3) gpsY:        위도(37.xxxxxx)
        (param4) radius:      검색 반경(default-150m, 정류장이 없을 때 50씩 증가)
        
        [return]
        arsIdList:            정류소 목록
        '''

        self.gpsX = gpsX
        self.gpsY = gpsY
        self.radius = radius

        while self.numStop == 0:
            request_Gps2Stop = API_STATION + "?serviceKey=" + self.serviceKey + "&tmX=" + str(gpsX) + "&tmY=" + str(gpsY) + "&radius=" + str(radius)
            xmlStation= urlopen(request_Gps2Stop)  # 출력 XML 텍스트

            bsStation = BeautifulSoup(xmlStation.read(), 'lxml-xml')    # Parsing XML

            headerCode = int(bsStation.findAll("headerCd").contents[0])
            if headerCode == 5:
                print(">>> 잘못된 경위도 입력") # Error event: To Input Wrong GPS 
                return None
            elif headerCode == 3:
                self.numStop = 0
                self.radius = self.radius + 50
                continue

            self.itemList = bsStation.findAll('itemList')
            self.numStop = len(self.itemList)
            if self.numStop == 0:                   # 찾은 정류장이 없으면
                if self.radius <= 1500:
                    self.radius = self.radius + 50
                    continue
                else:
                    self.numStop = 0
                    return None
            # 디버깅용 print문
            # print("주변 정류소 개수({}m): {}".format(self.radius, self.numItem))
            # print("반경 {}m 안 정류소 목록".format(self.radius))

            self.arsIdList = list(range(0, self.numStop))
            for i in range(0, self.numStop):
                # input arsIdList
                self.arsIdList[i] = self.itemList[i].find('arsId').contents[0]
            return self.arsIdList
      

    def __str__(self):
        self.arsIdStr = []
        for i in range(0, len(self.numStop)):
            self.arsIdStr.append(self.arsIdList[i]+' ')
        return self.arsIdStr



class BusRoute:
    '''
    정류소 ID를 입력받아 해당 정류소를 지나는 노선을 저장하는 클래스

    - 객체 생성 후, findRoute를 통해 노선 저장.

    [Members]
    
    arsId

    numStop
    itemList
    busRouteIdList

    [Methods]
    findRoute
    
    (CallBackURL: http://ws.bus.go.kr/api/rest/stationinfo/getRouteByStation)
    '''
    def __init__(self, serviceKey):
        '''
        공공 데이터 포털에서 발급받은 Service Key를 입력받아 초기화

        '''
        #초기화
        self.serviceKey = unquote(serviceKey)
        
        # 요청
        requestGPS2Stop = API_STATION + "?serviceKey=" + self.serviceKey # + "&arsId" + str(self.radius)
        xmlStation = urlopen(requestGPS2Stop)
        bsStation = BeautifulSoup(xmlStation.read(), 'lxml-xml')
        
        # URL 응답이 있는지 검사
        headerCode = int(bsStation.findAll("headerCd").contents[0])

        ## URL 체크
        if headerCode == 4 or headerCode == 0:
            print(">>> 정상 작동")
        else:
            print(">>> API 요청 오류")
        ## URL 체크


    def findRoute(self, arsId):
        self.arsId = arsId
        request_Stop2Route = API_STATION + "?serviceKey=" + self.serviceKey + "&arsId=" + arsId

        # 출력 XML 텍스트
        xmlRoute = urlopen(request_Stop2Route)

        # Parsing XML Busstop 
        bsRoute = BeautifulSoup(xmlRoute.read(), 'lxml-xml')

        self.itemList = bsRoute.findAll('itemList')
        self.numItem = len(self.itemList)
        # print("노선 개수: {}".format(self.numItem))

        self.busRouteIdList = list(range(self.numItem))
        for i in range(0,self.numItem):
            # input arsIdList
            self.busRouteIdList[i] = self.itemList[i].find('busRouteId').contents[0]
        return self.busRouteIdList

class BusRoutePath:
    '''
    버스 노선 ID를 받아 버스 경유 노선 목록을 저장하는 클래스

    - 객체 생성 후, findRoutePath로 실행하여 노선 목록 생성

    [Member]
    busRouteId

    numItem
    itemList

    busStationIdList

    [Method]
    findRoutePath(self, busRouteId)

    (CallBack URL: http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute)

    '''

    def __init__(self, serviceKey):
        '''
        공공 데이터 포털에서 발급받은 Service Key를 입력받아 초기
        '''

        #초기화
        self.serviceKey = unquote(serviceKey)
        
        requestRoutePath = API_ROUTE + "?serviceKey=" + serviceKey
        xmlRoutePath = urlopen(requestRoutePath)
        bsRoutePath = BeautifulSoup(xmlRoutePath.read(), 'lxml-xml')

        # URL 응답이 있는지 검사
        headerCode = int(bsRoutePath.find("headerCd").contents[0])

        ## URL 체크
        if headerCode == 4 or headerCode == 0:      # 요청 busRouteId가 없어 검색결과 없음(4)
            print(">>> 정상 작동")
        else:
            print(">>> API 요청 오류")
    
    def findRoutePath(self, busRouteId):
        # 입력 버스노선정보 저장
        self.busRouteId = busRouteId
        
        # API 요청 및 파싱
        requestRoutePath = API_ROUTE + "?serviceKey=" + self.serviceKey + "&busRouteId=" + busRouteId 
        xmlRoutePath = urlopen(requestRoutePath)
        bsRoutePath = BeautifulSoup(xmlRoutePath.read(), 'lxml-xml')

        self.itemList = bsRoutePath.findAll('itemList')
        self.numItem = len(self.itemList)

        self.busStationIdList = list(range(self.numItem))
        for i in range(0, self.numItem):
            # input arsIdList
            self.busStationIdList[i] = self.itemList[i].find('arsId').contents[0]
        return self.busStationIdList
